"""src.services.repo_fetcher
Service for fetching repository structure and file contents from various providers.
"""

from loguru import logger

from src.models.api_schema import WikiGenerationRequest
from src.models.wiki_schema import RepositoryStructure
from src.providers.base import RepositoryProvider
from src.providers.bitbucket import BitbucketProvider
from src.providers.github import GitHubProvider
from src.providers.gitlab import GitLabProvider
from src.providers.local import LocalProvider


class RepositoryFetcher:
    _PROVIDER_MAP: dict[str, type[RepositoryProvider]] = {
        "github": GitHubProvider,
        "gitlab": GitLabProvider,
        "bitbucket": BitbucketProvider,
        "local": LocalProvider,
    }

    def __init__(self, request: WikiGenerationRequest):
        self.request = request

        # 1. Determine and instantiate the provider at initialization
        # This avoids checking the mapping for every method call.
        provider_class = self._PROVIDER_MAP.get(self.request.repo_type)
        if not provider_class:
            raise ValueError(f"Unsupported repo type: {self.request.repo_type}")

        self.provider: RepositoryProvider = provider_class(self.request)

    async def fetch_repository_structure(self) -> RepositoryStructure:
        """Fetches the file tree structure of the repository."""
        logger.info(f"Fetching structure from {self.request.repo_type}...")
        return await self.provider.fetch_structure()

    async def fetch_file_content(self, file_path: str) -> str | None:
        """
        Fetches the content of a specific file.
        Called by WikiStructureDeterminer when generating page content.
        """
        logger.debug(f"Fetching file content: {file_path}")
        return await self.provider.fetch_file_content(file_path)

    async def close(self):
        """Method for resource cleanup."""
        if self.provider:
            await self.provider.close()

    # Support for Async Context Manager
    # Allows using 'async with RepositoryFetcher(...) as fetcher:' syntax
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
