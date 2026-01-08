import os
import sys

sys.path.append(os.getcwd())

from src.core.config import settings
from src.models.wiki_schema import WikiPage, WikiSection, WikiStructure
from src.services.notion_sync import sync_wiki_to_notion

# Mock data
page = WikiPage(
    id="test-page-1",
    title="Test Page",
    content="# Test Content\nThis is a test.",
    file_paths=["README.md"],
    importance="low",
    related_pages=[],
    parent_id="test-section-1",
)

section = WikiSection(
    id="test-section-1", title="Test Section", pages=["test-page-1"], subsections=[]
)

structure = WikiStructure(
    id="test-wiki",
    title="Test Wiki",
    description="Testing Notion Sync Fix",
    pages=[page],
    sections=[section],
    root_sections=["test-section-1"],
)

pages_content = {
    "test-page-1": """
# Test Document

Here is a table:

| Header 1 | Header 2 |
|---|---|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

Here are some links:
- [Valid Link](https://example.com)
- [WWW Link](www.google.com)
- [Relative Link](./local.md)
- [Bold Link](**https://bold.com**)
- **[Link inside bold](https://inner.com)**
- Text with [Link](https://example.com) inside.
- Text with [Broken Link] and (parentheses) separate.

"""
}

repo_name = "test-repo-verify"

try:
    # Print the masked ID to confirm what we are working with (first 4 chars)
    db_id = settings.NOTION_DATABASE_ID
    masked = db_id[:4] + "*" * (len(db_id) - 4) if db_id else "None"
    print(f"Using Database ID from settings: {masked}")

    result = sync_wiki_to_notion(
        repo_name=repo_name, structure=structure, pages_content=pages_content
    )
    print("Sync successful!")
    print(result)
except Exception as e:
    print(f"Sync failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
