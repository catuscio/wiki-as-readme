"""src.providers.local
Local filesystem repository provider implementation.
"""

import asyncio
import os
from pathlib import Path

from loguru import logger

from src.core.config import settings
from src.models.wiki_schema import RepositoryStructure
from src.providers.base import RepositoryProvider
from src.utils.file_filter import should_ignore


class LocalProvider(RepositoryProvider):
    def __init__(self, request):
        self.request = request
        self.client = None

    async def close(self):
        pass

    def _scan_disk_sync(self, local_path: str) -> tuple[str, str, str]:
        """[Synchronous Function] Performs disk scan (executed in a separate thread)."""
        repo_path = Path(local_path)
        if not repo_path.is_dir():
            raise FileNotFoundError(f"Local path does not exist: {local_path}")

        file_tree_list = []
        readme_content = ""

        try:
            for root, dirs, files in os.walk(repo_path):
                # Calculate relative path for filtering
                rel_root = Path(root).relative_to(repo_path)

                # Pruning: In-place modification of the directories list.
                # Filter out ignored directories
                dirs[:] = [
                    d
                    for d in dirs
                    if not should_ignore(str(rel_root / d), settings.IGNORED_PATTERNS)
                ]

                for file in files:
                    file_path = Path(root) / file
                    relative_path = str(file_path.relative_to(repo_path))

                    if should_ignore(relative_path, settings.IGNORED_PATTERNS):
                        continue

                    # Convert Windows paths (\) to POSIX (/) for consistency.
                    file_tree_list.append(relative_path.replace("\\", "/"))

            # Find README (requires additional logic for case-insensitivity, but typically README.md).
            readme_path = repo_path / "README.md"
            if readme_path.is_file():
                readme_content = readme_path.read_text(
                    encoding="utf-8", errors="ignore"
                )

            return "\n".join(sorted(file_tree_list)), readme_content, "main"

        except Exception as e:
            logger.error(f"Error scanning local disk: {e}")
            raise

    async def fetch_structure(self) -> RepositoryStructure:
        if not self.request.local_path:
            return RepositoryStructure(
                file_tree="",
                readme="",
                default_branch="main",
                error="Local path is not provided.",
            )

        try:
            # Offload CPU/Disk-bound tasks to a ThreadPool.
            file_tree, readme, branch = await asyncio.to_thread(
                self._scan_disk_sync, self.request.local_path
            )

            return RepositoryStructure(
                file_tree=file_tree, readme=readme, default_branch=branch
            )
        except Exception as e:
            return RepositoryStructure(
                file_tree="", readme="", default_branch="main", error=str(e)
            )

    async def fetch_file_content(self, file_path: str) -> str | None:
        if not self.request.local_path:
            return None

        try:
            full_path = Path(self.request.local_path) / file_path

            if full_path.is_file():
                return await asyncio.to_thread(
                    full_path.read_text, encoding="utf-8", errors="ignore"
                )

            logger.warning(f"Local file not found: {full_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading local file {file_path}: {e}")
            return None
