"""src.models.api_schema
Pydantic models for API request and response schemas.
"""

from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel, Field, model_validator


class WikiGenerationRequest(BaseModel):
    repo_owner: str | None = Field(
        None, description="The owner of the repository (user or organization)."
    )
    repo_name: str | None = Field(None, description="The name of the repository.")
    repo_type: Literal["github", "gitlab", "bitbucket", "local"] = Field(
        "github", description="The type of the repository."
    )
    repo_url: str | None = Field(
        None, description="The URL for cloning a remote repository."
    )
    local_path: str | None = Field(
        None, description="The local path to the repository if repo_type is 'local'."
    )
    language: str = Field(
        "ko", description="The language for the generated wiki content."
    )
    is_comprehensive_view: bool = Field(
        True, description="Whether to generate a comprehensive view of the repository."
    )

    @model_validator(mode="after")
    def derive_repo_details(self) -> "WikiGenerationRequest":
        # 1. Parse GitHub URL
        if self.repo_type == "github" and self.repo_url:
            self._parse_github_url()
        
        # 2. Derive name from local path if needed
        if self.repo_type == "local" and self.local_path and not self.repo_name:
            import os
            clean_path = self.local_path.strip().rstrip("/\\")
            basename = os.path.basename(clean_path)
            if basename.endswith(".git"):
                basename = basename[:-4]
            self.repo_name = basename

        return self

    def _parse_github_url(self):
        """Helper to extract owner and name from GitHub URL."""
        if not self.repo_url:
            return

        try:
            # Remove .git suffix and trailing slashes
            clean_url = self.repo_url.strip().rstrip("/").removesuffix(".git")

            # Split by '/'
            parts = clean_url.split("/")

            # Typical structure: https://github.com/{owner}/{name}
            if len(parts) >= 2:
                derived_owner = parts[-2]
                derived_name = parts[-1]

                if not self.repo_owner:
                    logger.debug(f"Derived repo_owner: {derived_owner}")
                    self.repo_owner = derived_owner

                if not self.repo_name:
                    logger.debug(f"Derived repo_name: {derived_name}")
                    self.repo_name = derived_name
        except Exception as e:
            logger.warning(f"Failed to parse GitHub URL: {e}")


class WikiGenerationResponse(BaseModel):
    message: str = Field(
        ..., description="A message indicating the status of the request."
    )
    task_id: str = Field(..., description="The ID of the background task initiated.")
    title: str = Field(..., description="The title of the generated wiki.")
    description: str = Field(..., description="The description of the generated wiki.")


class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="The ID of the task.")
    status: Literal["in_progress", "completed", "failed"] = Field(
        ..., description="Current status of the task."
    )
    result: Any | None = Field(
        None, description="Result of the task, if completed or failed."
    )
