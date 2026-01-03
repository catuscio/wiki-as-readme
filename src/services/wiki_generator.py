"""src.services.wiki_generator
Main service for coordinating the end-to-end wiki generation pipeline.
"""

import asyncio
import os

from loguru import logger

from src.models.api_schema import WikiGenerationRequest
from src.services.repo_fetcher import RepositoryFetcher
from src.services.structure_analyzer import WikiStructureDeterminer
from src.services.wiki_formatter import WikiFormatter


class WikiGenerationService:
    def __init__(self, request: WikiGenerationRequest):
        self.request = request

    @staticmethod
    def validate_request(request: WikiGenerationRequest):
        """Validates the request parameters."""
        if request.repo_type == "local" and not request.local_path:
            raise ValueError("For 'local' repo type, 'local_path' is required.")

        if request.repo_type == "github" and (
            not request.repo_owner or not request.repo_name
        ):
            raise ValueError(
                "For 'github' repo type, 'repo_owner' and 'repo_name' are required. "
                "Ensure repo_url is correctly formatted."
            )

    async def prepare_generation(self) -> WikiStructureDeterminer:
        """
        Initializes the determiner and fetches the initial structure.
        Useful for Human-in-the-loop flows where structure is confirmed before content generation.
        """
        return await self._initialize_and_determine()

    async def _wait_for_completion(self, determiner: WikiStructureDeterminer):
        """Helper to wait for the determiner to finish generation."""
        while determiner.is_loading or determiner.pages_in_progress:
            await asyncio.sleep(2)

        if determiner.error:
            raise RuntimeError(f"Wiki generation error: {determiner.error}")

    async def generate_wiki(
        self, determiner: WikiStructureDeterminer | None = None
    ) -> str:
        """
        Runs the full wiki generation pipeline.
        If a determiner is provided, it continues from that state (Human-in-the-loop).
        """
        # 1. Start from scratch if no determiner is provided (Auto-pilot)
        should_close_determiner = False
        if determiner is None:
            determiner = await self._initialize_and_determine()
            should_close_determiner = True

        # If the structure is determined, start content generation (unless it's already in progress or completed)
        if (
            not (determiner.is_loading or determiner.pages_in_progress)
            and not determiner.generated_pages
        ):
            await determiner.generate_contents(language=self.request.language)

        try:
            # 2. Wait for content generation
            await self._wait_for_completion(determiner)

            # 3. Verify structure (defensive code)
            if not determiner.wiki_structure:
                raise ValueError("Wiki structure is missing.")

            # 4. Merge results
            return WikiFormatter.consolidate_markdown(
                determiner.wiki_structure, determiner.generated_pages
            )
        finally:
            # Clean up resources if it's a newly created determiner
            if should_close_determiner:
                await determiner.close()

    async def _initialize_and_determine(self) -> WikiStructureDeterminer:
        """Initializes components and determines the wiki structure."""
        # 1. Get Repository Structure
        async with RepositoryFetcher(self.request) as fetcher:
            repo_struct = await fetcher.fetch_repository_structure()
            if repo_struct.error:
                raise ValueError(f"Repo fetch failed: {repo_struct.error}")

        # 2. Determine Repository Structure
        determiner = WikiStructureDeterminer(self.request)
        determiner.default_branch = repo_struct.default_branch

        await determiner.determine_wiki_structure(
            file_tree=repo_struct.file_tree,
            readme=repo_struct.readme,
            generate_contents=False,
        )

        if determiner.error:
            await determiner.close()
            raise ValueError(f"Structure determination failed: {determiner.error}")

        return determiner

    async def save_to_file(self, markdown_content: str) -> str:
        """Saves the markdown content to a file."""
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        repo_name = self.request.repo_name or "repository"
        safe_name = WikiFormatter.sanitize_filename(repo_name)
        file_path = os.path.join(output_dir, f"{safe_name}_README.md")

        try:
            # TODO: Consider using aiofiles for async process
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            logger.info(f"Wiki saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise OSError(f"File save error: {e}")
