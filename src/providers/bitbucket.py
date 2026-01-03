"""src.providers.bitbucket
Bitbucket-specific repository provider implementation using Bitbucket Cloud API.
"""

from loguru import logger

from src.core.config import settings
from src.models.wiki_schema import RepositoryStructure
from src.providers.base import RepositoryProvider
from src.utils.file_filter import should_ignore


class BitbucketProvider(RepositoryProvider):
    def _create_headers(self) -> dict[str, str]:
        headers = {}
        if settings.GIT_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GIT_API_TOKEN}"
        return headers

    async def fetch_structure(self) -> RepositoryStructure:
        headers = self._create_headers()
        base_url = "https://api.bitbucket.org/2.0/repositories"
        workspace = self.request.repo_owner
        repo_slug = self.request.repo_name

        default_branch = "master"
        file_list = []
        readme_content = ""

        try:
            # 1. Repository information
            repo_url = f"{base_url}/{workspace}/{repo_slug}"
            resp = await self.client.get(repo_url, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                if "mainbranch" in data:
                    default_branch = data["mainbranch"]["name"]

            # Store in an instance variable for later use when fetching files.
            self.default_branch = default_branch

            # 2. File tree
            src_url = f"{base_url}/{workspace}/{repo_slug}/src/{default_branch}/?recursive=true&pagelen=100"

            while src_url:
                resp = await self.client.get(src_url, headers=headers)
                if resp.status_code != 200:
                    break

                data = resp.json()
                values = data.get("values", [])

                file_list.extend(
                    [
                        item["path"]
                        for item in values
                        if item["type"] == "commit_file"
                        and not should_ignore(item["path"], settings.IGNORED_PATTERNS)
                    ]
                )

                src_url = data.get("next")

            # 3. README
            readme_url = (
                f"{base_url}/{workspace}/{repo_slug}/src/{default_branch}/README.md"
            )
            resp = await self.client.get(readme_url, headers=headers)
            if resp.status_code == 200:
                readme_content = resp.text

            return RepositoryStructure(
                file_tree="\n".join(file_list),
                readme=readme_content,
                default_branch=default_branch,
            )

        except Exception as e:
            logger.error(f"Bitbucket Fetch Error: {e}")
            return RepositoryStructure(
                file_tree="", readme="", default_branch="master", error=str(e)
            )

    async def fetch_file_content(self, file_path: str) -> str | None:
        """[Added] Fetch file content"""
        headers = self._create_headers()
        workspace = self.request.repo_owner
        repo_slug = self.request.repo_name

        # self.default_branch should exist if fetch_structure was called first,
        # but for safety, if it's missing, master or main could be tried, or an API call might be necessary.
        # Here, it is assumed fetch_structure ran first, or a default value is used.
        branch = getattr(self, "default_branch", "master")

        # The Bitbucket /src endpoint returns raw content for text files.
        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src/{branch}/{file_path}"

        try:
            resp = await self.client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.text

            logger.warning(
                f"Bitbucket fetch failed for {file_path}: {resp.status_code}"
            )
            return None
        except Exception as e:
            logger.error(f"Bitbucket file fetch error: {e}")
            return None
