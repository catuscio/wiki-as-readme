"""src.core.config
Configuration settings for the AX Wiki Generator using Pydantic Settings.
"""

import json
from typing import Any, Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_IGNORED_PATTERNS = [
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Gemfile.lock",
    "composer.lock",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    ".idea",
    ".vscode",
    ".DS_Store",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.svg",
    "*.ico",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.eot",
    "*.mp4",
    "*.webm",
    "*.mp3",
    "*.wav",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.rar",
    "*.7z",
    "*.pdf",
    "*.doc",
    "*.docx",
    "*.xls",
    "*.xlsx",
    "*.ppt",
    "*.pptx",
]


class Settings(BaseSettings):
    LLM_PROVIDER: Literal[
        "google", "openai", "anthropic", "openrouter", "xai", "ollama"
    ] = "google"
    MODEL_NAME: str = "gemini-2.5-flash"

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    XAI_API_KEY: str | None = None
    LLM_BASE_URL: str | None = None
    USE_STRUCTURED_OUTPUT: bool = True

    temperature: float = 0.0
    max_retries: int = 3
    max_concurrency: int = 5

    GIT_API_TOKEN: str | None = None

    language: (
        Literal["ko", "en", "ja", "zh", "zh-tw", "es", "vi", "pt-br", "fr", "ru"] | None
    ) = None

    # GCP
    GCP_PROJECT_NAME: str | None = None
    GCP_MODEL_LOCATION: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS: SecretStr | None = None

    IGNORED_PATTERNS: Any = DEFAULT_IGNORED_PATTERNS

    @field_validator("IGNORED_PATTERNS", mode="before")
    @classmethod
    def parse_ignored_patterns(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            if not v.strip():
                return DEFAULT_IGNORED_PATTERNS
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                return [s.strip() for s in v.split(",") if s.strip()]
        return v

    GITHUB_WEBHOOK_SECRET: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
