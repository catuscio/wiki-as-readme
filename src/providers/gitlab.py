"""src.providers.gitlab
GitLab-specific repository provider implementation supporting self-hosted instances.
"""

from urllib.parse import quote, urlparse

from loguru import logger

from src.core.config import settings
from src.models.wiki_schema import RepositoryStructure
from src.providers.base import RepositoryProvider
from src.utils.file_filter import should_ignore


class GitLabProvider(RepositoryProvider):
    def _create_headers(self) -> dict[str, str]:
        headers = {}
        if settings.GIT_API_TOKEN:
            headers["PRIVATE-TOKEN"] = settings.GIT_API_TOKEN
        return headers

    def _get_api_base(self) -> str:
        """
        Analyze URL to support self-hosted GitLab (on-premise).
        """
        if self.request.repo_url:
            parsed = urlparse(self.request.repo_url)
            # If a host is present and it is not gitlab.com, return the API path for that domain.
            if parsed.netloc and "gitlab.com" not in parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}/api/v4"

        return "https://gitlab.com/api/v4"

    def _get_encoded_project_path(self) -> str:
        """GitLab requires encoding 'owner/repo' as 'owner%2Frepo'."""
        full_path = f"{self.request.repo_owner}/{self.request.repo_name}"
        return quote(full_path, safe="")

    async def fetch_structure(self) -> RepositoryStructure:
        headers = self._create_headers()
        base_url = self._get_api_base()
        encoded_path = self._get_encoded_project_path()

        default_branch = "main"
        file_list = []
        readme_content = ""

        try:
            # 1. Project Information and Default Branch
            info_url = f"{base_url}/projects/{encoded_path}"
            resp = await self.client.get(info_url, headers=headers)

            if resp.status_code == 200:
                default_branch = resp.json().get("default_branch", "main")

            # 2. File Tree (Recursive + Pagination)
            page = 1
            per_page = 100
            while True:
                tree_url = (
                    f"{base_url}/projects/{encoded_path}/repository/tree"
                    f"?recursive=true&per_page={per_page}&page={page}&ref={default_branch}"
                )
                resp = await self.client.get(tree_url, headers=headers)

                if resp.status_code != 200:
                    logger.error(f"GitLab Tree Error: {resp.text}")
                    break

                items = resp.json()
                if not items:
                    break

                file_list.extend(
                    [
                        item["path"]
                        for item in items
                        if item["type"] == "blob"
                        and not should_ignore(item["path"], settings.IGNORED_PATTERNS)
                    ]
                )

                next_page = resp.headers.get("x-next-page")
                if not next_page:
                    break
                page = int(next_page)

            # 3. README (Raw File API)
            readme_url = f"{base_url}/projects/{encoded_path}/repository/files/README.md/raw?ref={default_branch}"
            resp = await self.client.get(readme_url, headers=headers)
            if resp.status_code == 200:
                readme_content = resp.text

            return RepositoryStructure(
                file_tree="\n".join(file_list),
                readme=readme_content,
                default_branch=default_branch,
            )

        except Exception as e:
            logger.error(f"GitLab Fetch Error: {e}")
            return RepositoryStructure(
                file_tree="", readme="", default_branch="main", error=str(e)
            )

    async def fetch_file_content(self, file_path: str) -> str | None:
        """[Added] Fetch file content"""
        base_url = self._get_api_base()
        encoded_project = self._get_encoded_project_path()
        headers = self._create_headers()

        # File path also needs URL encoding (e.g., src/main.py -> src%2Fmain.py)
        encoded_file_path = quote(file_path, safe="")

        # GitLab's 'raw' endpoint provides content as plain text.
        # Defaults to the default branch if ref (branch) is not specified, but explicit specification is safer.
        # For convenience, the default branch is assumed here. Ideally, the branch from the structure should be used,
        # but fetching based on HEAD is usually sufficient.
        url = f"{base_url}/projects/{encoded_project}/repository/files/{encoded_file_path}/raw"

        try:
            # Add ?ref=main or similar if the ref parameter is needed
            resp = await self.client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.text

            logger.warning(f"GitLab fetch failed for {file_path}: {resp.status_code}")
            return None
        except Exception as e:
            logger.error(f"GitLab file fetch error: {e}")
            return None
