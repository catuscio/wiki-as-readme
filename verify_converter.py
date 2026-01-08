import json
import os
import sys

sys.path.append(os.getcwd())

from src.services.notion_converter import NotionConverter

markdown_sample = """
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

blocks = NotionConverter.markdown_to_blocks(markdown_sample)
print(json.dumps(blocks, indent=2))
