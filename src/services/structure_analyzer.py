"""src.services.structure_analyzer
Service for determining wiki structure and generating content using LLMs.
"""

import asyncio
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template
from loguru import logger

from src.agent.llm import LLMWikiMaker
from src.core.config import settings
from src.models.api_schema import WikiGenerationRequest
from src.models.wiki_schema import WikiPage, WikiStructure
from src.services.repo_fetcher import RepositoryFetcher
from src.utils.generate_file_url import generate_file_url


class WikiStructureDeterminer:
    """Determines wiki structure and generates page contents using LLMs."""

    def __init__(
        self,
        request: WikiGenerationRequest,
        max_concurrency: int = settings.max_concurrency,
    ):
        self.request = request
        self.wiki_structure: WikiStructure | None = None
        self.current_page_id: str | None = None

        # State Management
        self.generated_pages: dict[str, str] = {}
        self.pages_in_progress: set[str] = set()
        self.error: str | None = None
        self.is_loading: bool = False
        self.loading_message: str | None = None
        self.structure_request_in_progress: bool = False
        self.default_branch: str = "main"

        # Fetcher maintains an internal httpx session.
        self.fetcher = RepositoryFetcher(self.request)
        self.llm_maker = LLMWikiMaker

        # Concurrency Control (Limit number of concurrent LLM requests)
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def close(self):
        """[Important] Must be called to clean up resources after use."""
        await self.fetcher.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @lru_cache(maxsize=10)
    def _load_prompt_template(self, prompt_path: str) -> tuple[str, list[str], str]:
        """Loads a prompt template from a YAML file (Cached)."""
        try:
            # Calculate relative path based on __file__
            base_path = Path(__file__).resolve().parent.parent
            full_path = base_path / prompt_path

            if not full_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {full_path}")

            with open(full_path, encoding="utf-8") as f:
                prompt_data: dict[str, Any] = yaml.safe_load(f)

            template: str = prompt_data.get("template", "")
            input_variables = [
                var["name"] if isinstance(var, dict) else var
                for var in prompt_data.get("input_variables", [])
            ]
            template_format = prompt_data.get("template_format", "jinja2")

            return template, input_variables, template_format
        except Exception as e:
            logger.error(f"Error loading prompt from {prompt_path}: {e}")
            raise

    async def _fetch_and_format_files(self, page: WikiPage) -> tuple[str, list[str]]:
        """
        [Improved] Fetches files in parallel using an asynchronous fetcher.
        """
        if not page.file_paths:
            return "", []

        # 1. Generate URLs (CPU-bound task)
        url_list = [
            generate_file_url(
                file_path=file_path,
                repo_type=self.request.repo_type,
                repo_url=self.request.repo_url,
                default_branch=self.default_branch,
            )
            for file_path in page.file_paths
        ]

        # 2. Fetch file contents (I/O-bound task - parallel processing)
        # RepositoryFetcher.fetch_file_content is asynchronous, so await is required.
        # Use asyncio.gather to request multiple files simultaneously.
        fetch_tasks = [
            self.fetcher.fetch_file_content(file_path) for file_path in page.file_paths
        ]

        # Results are returned as a list in the same order (may include None)
        contents = await asyncio.gather(*fetch_tasks)

        # 3. Content formatting
        content_list = []
        for file_path, content in zip(page.file_paths, contents):
            if content:
                content_list.append(f"--- {file_path} ---\n{content}\n")
            else:
                logger.warning(f"Skipping content for {file_path} (not found or empty)")

        return "\n".join(content_list), url_list

    async def generate_page_content(self, page: WikiPage, language: str = "en") -> None:
        """Generate individual page content with semaphore logic."""

        async with self.semaphore:  # Limit concurrent LLM calls
            logger.info(f"Generating content for page: {page.title}")
            try:
                prompt_template_str, input_vars, template_format = (
                    self._load_prompt_template("prompts/wiki_contents_generator.yaml")
                )

                template = Template(prompt_template_str)

                relevant_content, file_urls = await self._fetch_and_format_files(page)

                formatted_prompt = template.render(
                    pageTitle=page.title,
                    filePaths=file_urls,
                    relevant_source_files_content=relevant_content,
                    language=language,
                    use_structured_output=settings.USE_STRUCTURED_OUTPUT,
                )

                # 4. Get LLM Instance
                llm = LLMWikiMaker()
                generated_content = await llm.ainvoke(formatted_prompt)

                self.generated_pages[page.id] = generated_content
                logger.info(f"Completed: {page.title}")

            except Exception as e:
                logger.error(f"Error generating page {page.title}: {e}")
                self.generated_pages[page.id] = f"Error: {e}"
            finally:
                self.pages_in_progress.discard(page.id)

    async def determine_wiki_structure(
        self,
        file_tree: str,
        readme: str,
        default_branch: str | None = None,
        generate_contents: bool = True,
    ) -> WikiStructure | None:
        if self.structure_request_in_progress:
            logger.warning("Structure determination already in progress.")
            return None

        self.structure_request_in_progress = True
        self.is_loading = True
        self.loading_message = "Determining wiki structure..."
        self.error = None

        if default_branch:
            self.default_branch = default_branch

        try:
            prompt_template_str, input_vars, template_format = (
                self._load_prompt_template("prompts/wiki_structure_generator.yaml")
            )
            template = Template(prompt_template_str)

            llm = self.llm_maker(response_schema=WikiStructure)()

            formatted_prompt = template.render(
                owner=self.request.repo_owner,
                repo=self.request.repo_name,
                fileTree=file_tree,
                readme=readme,
                language=self.request.language,
                isComprehensiveView=self.request.is_comprehensive_view,
                use_structured_output=settings.USE_STRUCTURED_OUTPUT,
            )

            logger.info("Invoking LLM for structure...")

            wiki_structure = await llm.ainvoke(formatted_prompt)

            self.wiki_structure = wiki_structure
            self.current_page_id = (
                wiki_structure.pages[0].id if wiki_structure.pages else None
            )

            if generate_contents and wiki_structure.pages:
                # Execute as a background task
                asyncio.create_task(
                    self._start_content_generation_flow(language=self.request.language)
                )
            else:
                self.is_loading = False
                self.loading_message = None

            return wiki_structure

        except Exception as error:
            logger.error("Structure determination failed: {}", error, exc_info=True)
            self.error = str(error)
            self.is_loading = False
            return None
        finally:
            self.structure_request_in_progress = False

    async def _start_content_generation_flow(self, language: str):
        """Internal method to manage the full generation flow."""
        if not self.wiki_structure or not self.wiki_structure.pages:
            return

        self.pages_in_progress = {page.id for page in self.wiki_structure.pages}
        self.is_loading = True
        self.loading_message = (
            f"Generating content for {len(self.wiki_structure.pages)} pages..."
        )

        logger.info(self.loading_message)

        tasks = [
            self.generate_page_content(page, language)
            for page in self.wiki_structure.pages
        ]

        await self.run_page_generation_tasks(tasks)

    async def generate_contents(self, language: str):
        """Public method to start content generation (for compatibility)."""
        await self._start_content_generation_flow(language)

    async def run_page_generation_tasks(self, tasks: list):
        """Run tasks and cleanup."""
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("All generation tasks completed.")
        finally:
            self.is_loading = False
            self.loading_message = None
