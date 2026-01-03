"""src.services.wiki_formatter
Service for consolidating wiki structure and page content into markdown format.
"""

import re

from src.models.wiki_schema import WikiStructure


class WikiFormatter:
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize a string to be a valid filename."""
        sanitized_name = re.sub(r'[\\/*?:"<>|]', "", name)
        return sanitized_name.replace(" ", "_")

    @staticmethod
    def consolidate_markdown(structure: WikiStructure, pages: dict[str, str]) -> str:
        """Consolidate wiki structure and pages into a single markdown string."""
        content = [
            f"# {structure.title}\n",
            f"{structure.description}\n",
            "## Table of Contents\n",
        ]

        # Generate Table of Contents
        for page in structure.pages:
            anchor = (
                WikiFormatter.sanitize_filename(page.title).lower().replace("_", "-")
            )
            content.append(f"- [{page.title}](#{anchor})")
        content.append("\n---\n")

        # Generate Body Content
        for page in structure.pages:
            page_content = pages.get(page.id, "")
            anchor = (
                WikiFormatter.sanitize_filename(page.title).lower().replace("_", "-")
            )
            content.append(f'<a name="{anchor}"></a>\n')
            content.append(page_content)
            content.append("\n---\n")

        return "\n".join(content)
