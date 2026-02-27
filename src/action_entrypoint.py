"""
action_entrypoint.py
GitHub Action entrypoint for generating repository documentation (Wiki/README) using AI.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import src modules
sys.path.append(os.getcwd())

from loguru import logger

from src.core.config import settings
from src.models.api_schema import WikiGenerationRequest
from src.services.wiki_generator import WikiGenerationService


async def main():
    """
    Entrypoint for GitHub Action to generate Wiki/README.
    """
    # 1. Inputs from Settings (pydantic-settings reads environment variables automatically)
    local_path = settings.LOCAL_REPO_PATH
    output_path = Path(settings.WIKI_OUTPUT_PATH)
    language = settings.language

    # Notion sync settings
    notion_sync_enabled = settings.NOTION_SYNC_ENABLED
    notion_api_key = settings.NOTION_API_KEY
    notion_database_id = settings.NOTION_DATABASE_ID

    # Optional: Log the configuration (be careful not to log secrets)
    logger.info("Action triggered with:")
    logger.info(f"  Local Path (Source): {local_path}")
    logger.info(f"  Output Path: {output_path}")
    logger.info(f"  Language: {language}")
    logger.info(f"  Notion Sync: {notion_sync_enabled}")

    # 2. Construct Request
    # We use repo_type="local" because the Action checks out the code locally.
    request = WikiGenerationRequest(
        repo_type="local",
        local_path=local_path,
        repo_owner="action",  # Placeholder
        repo_name="action",  # Placeholder
        language=language,
        is_comprehensive_view=settings.IS_COMPREHENSIVE_VIEW,
    )

    # 3. Initialize Service and Generate
    service = WikiGenerationService(request)
    wiki_structure = None
    generated_pages = None

    try:
        logger.info("Starting Wiki Generation...")
        result = await service.generate_wiki_with_structure()

        markdown = result["markdown"]
        wiki_structure = result["structure"]
        generated_pages = result["pages"]

        if not markdown:
            logger.error("Generated content is empty.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # 4. Write Output
    os.makedirs(output_path.parent, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        logger.info(f"Successfully wrote wiki to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        sys.exit(1)

    # 5. Notion Sync (optional)
    if notion_sync_enabled and wiki_structure and generated_pages:
        if not notion_api_key or not notion_database_id:
            logger.warning(
                "Notion sync enabled but NOTION_API_KEY or "
                "NOTION_DATABASE_ID not set. Skipping."
            )
        else:
            try:
                from src.services.notion_sync import sync_wiki_to_notion

                # Use GITHUB_REPOSITORY env var if available, otherwise folder name
                github_repo = os.environ.get("GITHUB_REPOSITORY")
                if github_repo:
                    # GITHUB_REPOSITORY format: "owner/repo-name"
                    repo_name = github_repo.split("/")[-1]
                else:
                    repo_name = Path(local_path).resolve().name

                logger.info(f"Starting Notion sync for {repo_name}...")
                result_urls = sync_wiki_to_notion(
                    repo_name=repo_name,
                    structure=wiki_structure,
                    pages_content=generated_pages,
                    api_key=notion_api_key,
                    database_id=notion_database_id,
                )
                logger.info(f"Notion sync completed. Synced {len(result_urls)} pages.")
                for page_id, url in result_urls.items():
                    logger.info(f"  {page_id}: {url}")
            except ImportError:
                logger.warning(
                    "notion-client not installed. "
                    "Install with: pip install wiki-as-readme[notion]"
                )
            except Exception as e:
                logger.error(f"Notion sync failed: {e}")
                import traceback

                traceback.print_exc()
                # Don't exit - wiki file was already written successfully


if __name__ == "__main__":
    asyncio.run(main())
