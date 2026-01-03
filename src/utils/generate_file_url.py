"""src.utils.generate_file_url
Utility function for generating web URLs for files in various Git repository providers.
"""

import logging
from urllib.parse import urlparse


def generate_file_url(
    file_path: str, repo_type: str, repo_url: str | None, default_branch: str
) -> str:
    """
    Generate a web URL for a file in a Git repository.

    Args:
        file_path: The path to the file within the repository
        repo_type: Type of repository ('local' or 'remote')
        repo_url: The base URL of the repository
        default_branch: The default branch name (e.g., 'main', 'master')

    Returns:
        The complete URL to the file, or just the file_path if URL cannot be generated
    """
    if repo_type == "local":
        # For local repositories, we can't generate web URLs
        return file_path

    if not repo_url:
        return file_path

    try:
        parsed_url = urlparse(repo_url)
        hostname = parsed_url.hostname

        if not hostname:
            return file_path

        if hostname == "github.com" or "github" in hostname:
            # GitHub URL format: https://github.com/owner/repo/blob/branch/path
            return f"{repo_url}/blob/{default_branch}/{file_path}"

        if hostname == "gitlab.com" or "gitlab" in hostname:
            # GitLab URL format: https://gitlab.com/owner/repo/-/blob/branch/path
            return f"{repo_url}/-/blob/{default_branch}/{file_path}"

        if hostname == "bitbucket.org" or "bitbucket" in hostname:
            # Bitbucket URL format: https://bitbucket.org/owner/repo/src/branch/path
            return f"{repo_url}/src/{default_branch}/{file_path}"

    except Exception as error:
        logging.warning(f"Error generating file URL: {error}")

    # Fallback to just the file path
    return file_path
