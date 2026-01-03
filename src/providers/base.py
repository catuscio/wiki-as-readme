"""src.providers.base
Base abstract class for repository providers (GitHub, GitLab, etc.).
"""

from abc import ABC, abstractmethod

import httpx

from src.models.api_schema import WikiGenerationRequest
from src.models.wiki_schema import RepositoryStructure


class RepositoryProvider(ABC):
    def __init__(self, request: WikiGenerationRequest):
        self.request = request
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        """Resource cleanup"""
        await self.client.aclose()

    @abstractmethod
    async def fetch_structure(self) -> RepositoryStructure:
        """Method to fetch the file tree and README"""
        pass

    @abstractmethod
    async def fetch_file_content(self, file_path: str) -> str | None:
        """
        Method to fetch the content of a specific file.
        Specific logic must be implemented in each subclass (Local, GitHub, etc.).
        """
        pass
