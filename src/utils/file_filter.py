"""src.utils.file_filter
Utility for filtering files based on ignore patterns.
"""

import fnmatch
from pathlib import Path


def should_ignore(path: str, patterns: list[str]) -> bool:
    """
    Determines if a file path should be ignored based on a list of patterns.

    Args:
        path: The file path to check (relative path).
        patterns: List of glob patterns to ignore (e.g., ["*.pyc", "node_modules"]).

    Returns:
        True if the path matches any pattern, False otherwise.
    """
    if not patterns:
        return False

    # 1. Normalize path separators (Handle Windows backslashes)
    # path.replace("\", "/") -> Syntax Error! Fixed to "\\"
    normalized_path = path.replace("\\", "/")
    path_obj = Path(normalized_path)

    for pattern in patterns:
        # 1. Direct match with the full relative path (Most common)
        # e.g., pattern="src/temp/*", path="src/temp/file.txt"
        if fnmatch.fnmatch(normalized_path, pattern):
            return True

        # 2. Match against the file name
        # e.g., pattern="*.pyc", path="dir/test.pyc"
        if fnmatch.fnmatch(path_obj.name, pattern):
            return True

        # 3. Match against any directory component (Recursive check)
        # This handles filtering out entire directories regardless of depth.
        # e.g., pattern="node_modules", path="a/b/node_modules/c.js"
        # fnmatch is slightly expensive, so we check strictly for name matches first if possible
        if pattern in path_obj.parts:
            return True

        # If the pattern contains wildcards, we need fnmatch for parts
        if any(fnmatch.fnmatch(part, pattern) for part in path_obj.parts):
            return True

    return False
