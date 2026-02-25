"""src.services.notion_sync
Service for synchronizing wiki content to Notion database and pages.
"""

import re
from typing import Any, cast

from loguru import logger

from src.core.config import settings
from src.models.wiki_schema import WikiStructure
from src.services.notion_converter import NotionConverter

try:
    import httpx
    from notion_client import Client as NotionClient
    from notion_client.errors import APIResponseError, HTTPResponseError

    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    NotionClient = None  # type: ignore[misc, assignment]
    APIResponseError = Exception  # type: ignore[misc, assignment]
    HTTPResponseError = Exception  # type: ignore[misc, assignment]
    httpx = None  # type: ignore[misc, assignment]

NOTION_API_VERSION = "2022-06-28"


class NotionSyncService:
    """Synchronizes wiki content to Notion database."""

    def __init__(
        self,
        api_key: str | None = None,
        database_id: str | None = None,
    ):
        if not NOTION_AVAILABLE:
            raise ImportError(
                "notion-client is not installed. "
                "Install it with: pip install notion-client"
            )

        self.api_key = api_key or settings.NOTION_API_KEY
        self.database_id = database_id or settings.NOTION_DATABASE_ID

        if self.database_id:
            match = re.search(r"([a-f0-9]{32})", self.database_id)
            if match:
                self.database_id = match.group(1)

        if not self.api_key:
            raise ValueError("NOTION_API_KEY is required for Notion sync")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID is required for Notion sync")

        self.client = NotionClient(auth=self.api_key)
        self.converter = NotionConverter()
        self._title_property_name: str | None = None

    def sync_wiki(
        self,
        repo_name: str,
        structure: WikiStructure,
        pages_content: dict[str, str],
    ) -> dict[str, str]:
        """Sync wiki to Notion database."""
        logger.info(f"Starting Notion sync for repo: {repo_name}")

        # 1. Find or create repo item in database
        repo_page_id = self._upsert_database_item(repo_name)
        logger.info(f"Repo page ready: {repo_name}")

        # 2. Clear existing content (archive child pages, delete other blocks)
        self._clear_existing_content(repo_page_id)

        # 3. Add intro blocks
        intro_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"type": "text", "text": {"content": structure.title[:2000]}}
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": structure.description[:2000]},
                        }
                    ]
                },
            },
            {"object": "block", "type": "divider", "divider": {}},
        ]
        self._append_blocks_safe(repo_page_id, intro_blocks)

        # Build lookup maps
        page_map = {p.id: p for p in structure.pages}
        section_map = {s.id: s for s in structure.sections}

        result_urls: dict[str, str] = {}

        # 4. Process each root section - create pages directly under repo page
        for section_id in structure.root_sections:
            section = section_map.get(section_id)
            if not section:
                continue

            # Create pages directly under repo page (no intermediate section page)
            for page_id in section.pages:
                page = page_map.get(page_id)
                if not page:
                    continue

                markdown_content = pages_content.get(page_id, page.content)
                blocks = self.converter.markdown_to_blocks(markdown_content)

                if page.file_paths:
                    source_block = self._create_source_files_block(page.file_paths)
                    blocks.insert(0, source_block)

                page_notion_id = self._create_page(
                    parent_id=repo_page_id,
                    title=page.title,
                )
                self._append_blocks_safe(page_notion_id, blocks)

                result_urls[page_id] = self._get_page_url(page_notion_id)
                logger.info(f"Synced page: {page.title}")

            # Handle subsections - also create pages directly under repo page
            if section.subsections:
                for subsection_id in section.subsections:
                    subsection_urls = self._sync_subsection_flat(
                        subsection_id=subsection_id,
                        parent_notion_id=repo_page_id,
                        section_map=section_map,
                        page_map=page_map,
                        pages_content=pages_content,
                    )
                    result_urls.update(subsection_urls)

        logger.info(f"Notion sync completed. Synced {len(result_urls)} pages.")
        return result_urls

    def _get_notion_headers(self) -> dict[str, str]:
        """Get headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    def _get_title_property_name(self) -> str:
        """Get the name of the title property from the database schema."""
        if self._title_property_name:
            return self._title_property_name

        try:
            resp = httpx.get(
                f"https://api.notion.com/v1/databases/{self.database_id}",
                headers=self._get_notion_headers(),
            )
            resp.raise_for_status()

            data = cast("dict[str, Any]", resp.json())
            properties = data.get("properties", {})

            for name, prop in properties.items():
                if prop.get("type") == "title":
                    self._title_property_name = name
                    logger.info(f"Title property: {name}")
                    return name

            return "Name"
        except Exception as e:
            logger.warning(f"Failed to fetch DB schema: {e}")
            return "Name"

    def _upsert_database_item(self, repo_name: str) -> str:
        """Find or create a database item for the repository."""
        title_prop = self._get_title_property_name()

        # Search for existing item
        try:
            resp = httpx.post(
                f"https://api.notion.com/v1/databases/{self.database_id}/query",
                headers=self._get_notion_headers(),
                json={
                    "filter": {"property": title_prop, "title": {"equals": repo_name}}
                },
            )
            resp.raise_for_status()

            data = cast("dict[str, Any]", resp.json())
            results = data.get("results", [])

            if results:
                page_id = results[0]["id"]
                logger.info(f"Found existing DB item: {repo_name}")
                return str(page_id)
        except Exception as e:
            logger.warning(f"Query failed: {e}")

        # Create new item
        response = cast("dict[str, Any]", self.client.pages.create(
            parent={"database_id": self.database_id},
            properties={title_prop: {"title": [{"text": {"content": repo_name}}]}},
        ))
        logger.info(f"Created DB item: {repo_name}")
        return str(response["id"])

    def _clear_existing_content(self, page_id: str) -> None:
        """Clear all content from the page (archive child pages, delete blocks)."""
        try:
            has_more = True
            start_cursor = None

            while has_more:
                response = cast("dict[str, Any]", self.client.blocks.children.list(
                    block_id=page_id, start_cursor=start_cursor
                ))

                blocks = response.get("results", [])
                for block in blocks:
                    block_id = block["id"]
                    if block.get("type") == "child_page":
                        # Archive the page
                        self.client.pages.update(page_id=block_id, archived=True)
                    else:
                        # Delete the block
                        self.client.blocks.delete(block_id=block_id)

                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")

        except Exception as e:
            logger.warning(f"Failed to clear page content: {e}")

    def _sync_subsection_flat(
        self,
        subsection_id: str,
        parent_notion_id: str,
        section_map: dict,
        page_map: dict,
        pages_content: dict[str, str],
    ) -> dict[str, str]:
        """Recursively sync subsection pages directly under parent (flat structure)."""
        section = section_map.get(subsection_id)
        if not section:
            return {}

        result_urls: dict[str, str] = {}

        # Create pages directly under parent (no intermediate section page)
        for page_id in section.pages:
            page = page_map.get(page_id)
            if not page:
                continue

            markdown_content = pages_content.get(page_id, page.content)
            blocks = self.converter.markdown_to_blocks(markdown_content)

            if page.file_paths:
                source_block = self._create_source_files_block(page.file_paths)
                blocks.insert(0, source_block)

            page_notion_id = self._create_page(
                parent_id=parent_notion_id,
                title=page.title,
            )
            self._append_blocks_safe(page_notion_id, blocks)

            result_urls[page_id] = self._get_page_url(page_notion_id)

        # Handle nested subsections - also flat
        if section.subsections:
            for nested_id in section.subsections:
                nested_urls = self._sync_subsection_flat(
                    subsection_id=nested_id,
                    parent_notion_id=parent_notion_id,
                    section_map=section_map,
                    page_map=page_map,
                    pages_content=pages_content,
                )
                result_urls.update(nested_urls)

        return result_urls

    def _create_page(self, parent_id: str, title: str) -> str:
        """Create a new Notion page."""
        response = cast("dict[str, Any]", self.client.pages.create(
            parent={"page_id": parent_id},
            properties={"title": {"title": [{"text": {"content": title[:2000]}}]}},
        ))
        return str(response["id"])

    def _append_blocks_safe(self, page_id: str, blocks: list[dict[str, Any]]) -> None:
        """Append blocks with automatic retry on payload too large."""
        if not blocks:
            return

        batch_size = 10  # Start with small batch

        i = 0
        while i < len(blocks):
            batch = blocks[i : i + batch_size]
            try:
                self.client.blocks.children.append(block_id=page_id, children=batch)
                i += batch_size
            except (APIResponseError, HTTPResponseError) as e:
                error_str = str(e)
                if "413" in error_str or "Payload Too Large" in error_str:
                    if batch_size > 1:
                        # Reduce batch size and retry
                        batch_size = max(1, batch_size // 2)
                        logger.warning(f"Reducing batch size to {batch_size}")
                        continue
                    # Single block too large - skip it
                    logger.error(f"Block too large, skipping: {e}")
                    i += 1
                else:
                    logger.error(f"Failed to append: {e}")
                    i += batch_size  # Skip this batch

    def _get_page_url(self, page_id: str) -> str:
        """Get the URL for a Notion page."""
        clean_id = page_id.replace("-", "")
        return f"https://notion.so/{clean_id}"

    def _create_source_files_block(self, file_paths: list[str]) -> dict[str, Any]:
        """Create a toggle block showing source files."""
        file_list = "\n".join(f"- {path}" for path in file_paths[:50])  # Limit files
        if len(file_list) > 2000:
            file_list = file_list[:1997] + "..."

        return {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Relevant source files"},
                        "annotations": {"bold": True},
                    }
                ],
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": file_list}}
                            ]
                        },
                    }
                ],
            },
        }


def sync_wiki_to_notion(
    repo_name: str,
    structure: WikiStructure,
    pages_content: dict[str, str],
    api_key: str | None = None,
    database_id: str | None = None,
) -> dict[str, str]:
    """Convenience function to sync wiki to Notion database."""
    service = NotionSyncService(api_key=api_key, database_id=database_id)
    return service.sync_wiki(repo_name, structure, pages_content)
