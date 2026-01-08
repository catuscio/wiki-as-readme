"""src.services.notion_converter
Converts markdown content to Notion API block format.
"""

import re
from typing import Any


class NotionConverter:
    """Converts markdown to Notion blocks."""

    @staticmethod
    def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
        """Convert markdown string to a list of Notion blocks."""
        blocks: list[dict[str, Any]] = []
        lines = markdown.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Divider
            if line.strip() in ("---", "***", "___"):
                blocks.append({"object": "block", "type": "divider", "divider": {}})
                i += 1
                continue

            # Table block
            if line.strip().startswith("|"):
                table_block, consumed = NotionConverter._parse_table_block(lines, i)
                if table_block:
                    blocks.append(table_block)
                    i += consumed
                    continue

            # Code block
            if line.strip().startswith("```"):
                code_blocks, consumed = NotionConverter._parse_code_block(lines, i)
                blocks.extend(code_blocks)
                i += consumed
                continue

            # Details/Toggle block
            if line.strip().startswith("<details>"):
                block, consumed = NotionConverter._parse_details_block(lines, i)
                if block:
                    blocks.append(block)
                i += consumed
                continue

            # Headings
            heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                heading_type = f"heading_{level}"
                blocks.append(
                    {
                        "object": "block",
                        "type": heading_type,
                        heading_type: {
                            "rich_text": NotionConverter._parse_rich_text(text)
                        },
                    }
                )
                i += 1
                continue

            # Numbered list
            numbered_match = re.match(r"^\d+\.\s+(.+)$", line)
            if numbered_match:
                text = numbered_match.group(1)
                blocks.append(
                    {
                        "object": "block",
                        "type": "numbered_list_item",
                        "numbered_list_item": {
                            "rich_text": NotionConverter._parse_rich_text(text)
                        },
                    }
                )
                i += 1
                continue

            # Bullet list
            bullet_match = re.match(r"^[-*]\s+(.+)$", line)
            if bullet_match:
                text = bullet_match.group(1)
                blocks.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": NotionConverter._parse_rich_text(text)
                        },
                    }
                )
                i += 1
                continue

            # Anchor tag (skip)
            if line.strip().startswith("<a name="):
                i += 1
                continue

            # Regular paragraph
            if line.strip():
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": NotionConverter._parse_rich_text(line)
                        },
                    }
                )
            i += 1

        return blocks

    # Notion API limit for text content in a single block
    MAX_TEXT_LENGTH = 2000

    @staticmethod
    def _parse_table_block(
        lines: list[str], start: int
    ) -> tuple[dict[str, Any] | None, int]:
        """Parse a markdown table into a Notion table block."""
        table_lines = []
        i = start

        # Collect table lines
        while i < len(lines) and lines[i].strip().startswith("|"):
            table_lines.append(lines[i])
            i += 1

        consumed = i - start

        # Need at least header and separator
        if len(table_lines) < 2:
            return None, 0  # Not a valid table, let main loop handle as text

        # Parse rows
        rows = []
        for line in table_lines:
            # Remove leading/trailing pipes and split
            content = line.strip().strip("|")
            cells = [cell.strip() for cell in content.split("|")]
            rows.append(cells)

        # Check for separator line (usually 2nd line, contains only - and | and :)
        separator = rows[1]
        is_valid_separator = all(re.match(r"^[-:]+$", cell) for cell in separator)

        if not is_valid_separator:
            # Maybe not a table? Or headerless? Notion tables require headers.
            # If strictly markdown, 2nd line MUST be separator.
            return None, 0

        # Remove separator from data
        header_row = rows[0]
        data_rows = rows[2:]

        # Ensure all rows have same number of columns as header
        width = len(header_row)
        table_rows_blocks = []

        # Helper to create row block
        def create_row_block(cells: list[str]) -> dict[str, Any]:
            # Pad or truncate cells to match width
            current_cells = cells[:width] + [""] * (width - len(cells))
            return {
                "type": "table_row",
                "table_row": {
                    "cells": [
                        NotionConverter._parse_rich_text(cell) for cell in current_cells
                    ]
                },
            }

        # Add header
        table_rows_blocks.append(create_row_block(header_row))

        # Add data
        for row in data_rows:
            table_rows_blocks.append(create_row_block(row))

        return {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": width,
                "has_column_header": True,
                "has_row_header": False,
                "children": table_rows_blocks,
            },
        }, consumed

    @staticmethod
    def _parse_code_block(
        lines: list[str], start: int
    ) -> tuple[list[dict[str, Any]], int]:
        """Parse a code block and return (blocks, lines_consumed).

        If code exceeds 2000 chars, splits into multiple blocks.
        """
        first_line = lines[start].strip()
        # Extract language from ```language
        lang_match = re.match(r"^```(\w*)$", first_line)
        language = lang_match.group(1) if lang_match else "plain text"
        if not language:
            language = "plain text"

        # Notion supported languages
        supported_languages = {
            "abap",
            "abc",
            "agda",
            "arduino",
            "ascii art",
            "assembly",
            "bash",
            "basic",
            "bnf",
            "c",
            "c#",
            "c++",
            "clojure",
            "coffeescript",
            "coq",
            "css",
            "dart",
            "dhall",
            "diff",
            "docker",
            "ebnf",
            "elixir",
            "elm",
            "erlang",
            "f#",
            "flow",
            "fortran",
            "gherkin",
            "glsl",
            "go",
            "graphql",
            "groovy",
            "haskell",
            "hcl",
            "html",
            "idris",
            "java",
            "javascript",
            "json",
            "julia",
            "kotlin",
            "latex",
            "less",
            "lisp",
            "livescript",
            "llvm ir",
            "lua",
            "makefile",
            "markdown",
            "markup",
            "matlab",
            "mathematica",
            "mermaid",
            "nix",
            "notion formula",
            "objective-c",
            "ocaml",
            "pascal",
            "perl",
            "php",
            "plain text",
            "powershell",
            "prolog",
            "protobuf",
            "purescript",
            "python",
            "r",
            "racket",
            "reason",
            "ruby",
            "rust",
            "sass",
            "scala",
            "scheme",
            "scss",
            "shell",
            "smalltalk",
            "solidity",
            "sql",
            "swift",
            "toml",
            "typescript",
            "vb.net",
            "verilog",
            "vhdl",
            "visual basic",
            "webassembly",
            "xml",
            "yaml",
            "java/c/c++/c#",
        }

        # Map common language names to Notion's supported languages
        lang_map = {
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "sh": "shell",
            "yml": "yaml",
            "md": "markdown",
            "dockerfile": "docker",
            "env": "plain text",
            "dotenv": "plain text",
            "txt": "plain text",
            "text": "plain text",
            "csv": "plain text",
            "log": "plain text",
            "conf": "plain text",
            "cfg": "plain text",
            "ini": "plain text",
        }
        language = lang_map.get(language.lower(), language.lower())

        # Fallback to plain text if language is not supported
        if language not in supported_languages:
            language = "plain text"

        code_lines = []
        i = start + 1
        while i < len(lines) and not lines[i].strip().startswith("```"):
            code_lines.append(lines[i])
            i += 1

        # Skip closing ```
        consumed = i - start + 1

        code_content = "\n".join(code_lines)

        # Split into multiple blocks if content exceeds limit
        blocks: list[dict[str, Any]] = []
        max_len = NotionConverter.MAX_TEXT_LENGTH

        if len(code_content) <= max_len:
            blocks.append(
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {"type": "text", "text": {"content": code_content}}
                        ],
                        "language": language,
                    },
                }
            )
        else:
            # Split by lines to avoid cutting mid-line
            current_chunk = ""
            for line in code_lines:
                if len(current_chunk) + len(line) + 1 > max_len:
                    if current_chunk:
                        blocks.append(
                            {
                                "object": "block",
                                "type": "code",
                                "code": {
                                    "rich_text": [
                                        {
                                            "type": "text",
                                            "text": {"content": current_chunk.rstrip()},
                                        }
                                    ],
                                    "language": language,
                                },
                            }
                        )
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"

            # Add remaining content
            if current_chunk.strip():
                blocks.append(
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": current_chunk.rstrip()},
                                }
                            ],
                            "language": language,
                        },
                    }
                )

        return blocks, consumed

    @staticmethod
    def _parse_details_block(
        lines: list[str], start: int
    ) -> tuple[dict[str, Any] | None, int]:
        """Parse a <details> block into a Notion toggle block."""
        summary = ""
        content_lines = []
        i = start

        # Find summary
        while i < len(lines):
            line = lines[i]
            if "<summary>" in line:
                summary_match = re.search(r"<summary>(.+?)</summary>", line)
                if summary_match:
                    summary = summary_match.group(1)
            elif "</details>" in line:
                i += 1
                break
            elif not line.strip().startswith("<"):
                content_lines.append(line)
            i += 1

        consumed = i - start
        if not summary:
            return None, consumed

        # Parse inner content as child blocks
        inner_content = "\n".join(content_lines)
        children = NotionConverter.markdown_to_blocks(inner_content)

        return {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": NotionConverter._parse_rich_text(summary),
                "children": children if children else [],
            },
        }, consumed

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL is valid for Notion (must be absolute http/https)."""
        if not url:
            return False
        # Allow www. by prepending https:// (handled in caller usually, but here we just validate)
        # Actually, caller needs to modify it. _parse_rich_text needs to handle this.
        # Here we just return True if it looks like a URL we can fix or use.
        if url.startswith("www."):
            return True
        return url.startswith("http://") or url.startswith("https://")

    @staticmethod
    def _parse_rich_text(text: str) -> list[dict[str, Any]]:
        """Parse markdown inline formatting to Notion rich_text format."""
        result: list[dict[str, Any]] = []

        # Pattern to match: **bold**, *italic*, `code`, [link](url)
        # Removed the catch-all group to avoid skipping text
        pattern = r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\))"

        last_end = 0

        for match in re.finditer(pattern, text):
            # Append plain text occurring before this match
            if match.start() > last_end:
                result.append(
                    {
                        "type": "text",
                        "text": {"content": text[last_end : match.start()]},
                    }
                )

            # Process the match
            if match.group(2):  # Bold
                result.append(
                    {
                        "type": "text",
                        "text": {"content": match.group(2)},
                        "annotations": {"bold": True},
                    }
                )
            elif match.group(3):  # Italic
                result.append(
                    {
                        "type": "text",
                        "text": {"content": match.group(3)},
                        "annotations": {"italic": True},
                    }
                )
            elif match.group(4):  # Inline code
                result.append(
                    {
                        "type": "text",
                        "text": {"content": match.group(4)},
                        "annotations": {"code": True},
                    }
                )
            elif match.group(5) and match.group(6):  # Link
                link_text = match.group(5)
                link_url = match.group(6)

                # Fix common URL issues
                if link_url.startswith("www."):
                    link_url = f"https://{link_url}"

                if NotionConverter._is_valid_url(link_url):
                    result.append(
                        {
                            "type": "text",
                            "text": {
                                "content": link_text,
                                "link": {"url": link_url},
                            },
                        }
                    )
                else:
                    # Invalid URL (anchor, relative path) - render as plain text
                    # but keep the text content
                    result.append(
                        {
                            "type": "text",
                            "text": {"content": link_text},
                        }
                    )

            last_end = match.end()

        # Append any remaining plain text
        if last_end < len(text):
            result.append({"type": "text", "text": {"content": text[last_end:]}})

        # Fallback for empty/no-match cases (though logic above handles no-match)
        if not result and text:
            result.append({"type": "text", "text": {"content": text}})

        return result
