"""src.models.github_webhook_schema
Pydantic models for GitHub webhook push payloads.
"""

from pydantic import BaseModel


class GitHubRepositoryOwner(BaseModel):
    login: str


class GitHubRepository(BaseModel):
    name: str
    owner: GitHubRepositoryOwner


class GitHubPusher(BaseModel):
    name: str
    email: str | None = None


class GitHubCommit(BaseModel):
    id: str
    message: str
    author: GitHubPusher | None = None


class GitHubPushPayload(BaseModel):
    ref: str
    repository: GitHubRepository
    pusher: GitHubPusher | None = None
    head_commit: GitHubCommit | None = None
