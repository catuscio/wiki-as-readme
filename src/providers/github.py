"""src.providers.github
GitHub-specific repository provider implementation using GitHub REST API.
"""

import base64

from loguru import logger

from src.core.config import settings
from src.models.wiki_schema import RepositoryStructure
from src.providers.base import RepositoryProvider
from src.utils.file_filter import should_ignore


class GitHubProvider(RepositoryProvider):
    def _create_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Wiki-Generator-Bot",
        }
        if settings.GIT_API_TOKEN:
            headers["Authorization"] = f"token {settings.GIT_API_TOKEN}"
        return headers

    def _get_api_base(self) -> str:
        return "https://api.github.com"

    async def fetch_structure(self) -> RepositoryStructure:
        headers = self._create_headers()
        base_url = self._get_api_base()
        owner, repo = self.request.repo_owner, self.request.repo_name

        default_branch = "main"
        file_tree = ""
        readme_content = ""

        try:
            # 1. Get default branch information
            repo_info_url = f"{base_url}/repos/{owner}/{repo}"
            resp = await self.client.get(repo_info_url, headers=headers)

            if resp.status_code == 200:
                default_branch = resp.json().get("default_branch", "main")

            # 2. Fetch file tree (Recursive)
            tree_url = f"{base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            resp = await self.client.get(tree_url, headers=headers)

            if resp.status_code == 200:
                tree_data = resp.json()
                paths = [
                    item["path"]
                    for item in tree_data.get("tree", [])
                    if item["type"] == "blob"
                    and not should_ignore(item["path"], settings.IGNORED_PATTERNS)
                ]
                file_tree = "\n".join(paths)
            else:
                logger.error(f"Failed to fetch tree: {resp.text}")

            # 3. Fetch README (using API endpoint)
            # The /repos/{owner}/{repo}/readme endpoint automatically finds the file name (e.g., .md, .txt).
            readme_api_url = f"{base_url}/repos/{owner}/{repo}/readme"
            resp = await self.client.get(readme_api_url, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                # GitHub API provides content in Base64 format.
                if "content" in data:
                    readme_content = base64.b64decode(data["content"]).decode("utf-8")
            elif resp.status_code == 404:
                logger.info("No README found in this repository.")
            else:
                logger.warning(f"Failed to fetch README: {resp.status_code}")

            return RepositoryStructure(
                file_tree=file_tree,
                readme=readme_content,
                default_branch=default_branch,
            )

        except Exception as e:
            logger.error(f"GitHub Fetch Error: {e}")
            return RepositoryStructure(
                file_tree="", readme="", default_branch=default_branch, error=str(e)
            )

    async def fetch_file_content(self, file_path: str) -> str | None:
        github_api_base = self._get_api_base()
        headers = self._create_headers()

        api_url = f"{github_api_base}/repos/{self.request.repo_owner}/{self.request.repo_name}/contents/{file_path}"

        try:
            response = await self.client.get(api_url, headers=headers)

            if response.status_code == 200:
                file_data = response.json()
                if "content" in file_data:
                    encoded_content = file_data["content"]
                    return base64.b64decode(encoded_content).decode("utf-8")

                logger.warning(f"No content found for '{file_path}'")
                return None
            logger.warning(
                f"Could not fetch file '{file_path}'. Status: {response.status_code}"
            )
            return None
        except Exception as e:
            logger.error(f"Error fetching file '{file_path}': {e}")
            return None
