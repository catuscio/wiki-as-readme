"""src.agent.llm
LLM Wrapper using LiteLLM for Wiki Generation Tasks.
"""

import os

os.environ["LITELLM_LOG"] = "ERROR"

from typing import Any, TypeVar

import litellm
from pydantic import BaseModel

from src.core.config import settings

# Disable LiteLLM verbose logging and cost tracking
litellm.set_verbose = False
litellm.disable_spend_logs = True
litellm.disable_spend_updates = True
litellm.disable_end_user_cost_tracking = True

T = TypeVar("T", bound=BaseModel)


class LLMWikiMaker[T: BaseModel]:
    """
    Wrapper for LiteLLM to perform wiki generation tasks.
    Supports Structured Output with Type Safety via Generics.
    """

    def __init__(self, response_schema: type[T] | None = None):
        self.response_schema = response_schema
        self.model_name, self.completion_kwargs = self._configure_llm()

    def _configure_llm(self) -> tuple[str, dict]:
        """
        Configures the model name and arguments based on the provider settings.
        Handles provider-specific prefixes and environment variables.
        """
        provider = settings.LLM_PROVIDER.lower()
        base_model = settings.MODEL_NAME

        # Global Settings
        kwargs = {
            "temperature": settings.temperature,
            "max_retries": settings.max_retries,
            "timeout": settings.llm_timeout,
        }

        # 1. Google Vertex AI
        if provider == "google":
            if not base_model.startswith("vertex_ai/"):
                full_model_name = f"vertex_ai/{base_model}"
            else:
                full_model_name = base_model

            kwargs["vertex_project"] = settings.GCP_PROJECT_NAME
            kwargs["vertex_location"] = settings.GCP_MODEL_LOCATION
            return full_model_name, kwargs

        # 2. OpenAI (GPT)
        if provider == "openai":
            if not settings.OPENAI_API_KEY and not settings.LLM_BASE_URL:
                raise ValueError(
                    "Either OPENAI_API_KEY or LLM_BASE_URL must be set for OpenAI provider."
                )

            # [Fix 2] SIM102: Merge nested if statements into one
            if settings.OPENAI_API_KEY and "OPENAI_API_KEY" not in os.environ:
                os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

            if settings.LLM_BASE_URL:
                kwargs["api_base"] = settings.LLM_BASE_URL

            if not base_model.startswith("openai/"):
                full_model_name = f"openai/{base_model}"
            else:
                full_model_name = base_model
            return full_model_name, kwargs

        # 3. Anthropic (Claude)
        if provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError(
                    "ANTHROPIC_API_KEY is not set in environment variables."
                )

            if "ANTHROPIC_API_KEY" not in os.environ:
                os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

            if not base_model.startswith("anthropic/"):
                full_model_name = f"anthropic/{base_model}"
            else:
                full_model_name = base_model
            return full_model_name, kwargs

        # 4. OpenRouter
        if provider == "openrouter":
            if not settings.OPENROUTER_API_KEY:
                raise ValueError(
                    "OPENROUTER_API_KEY is not set in environment variables."
                )

            if "OPENROUTER_API_KEY" not in os.environ:
                os.environ["OPENROUTER_API_KEY"] = settings.OPENROUTER_API_KEY

            if not base_model.startswith("openrouter/"):
                full_model_name = f"openrouter/{base_model}"
            else:
                full_model_name = base_model
            return full_model_name, kwargs

        # 5. xAI (Grok)
        if provider == "xai":
            if not settings.XAI_API_KEY:
                raise ValueError("XAI_API_KEY is not set in environment variables.")

            if "XAI_API_KEY" not in os.environ:
                os.environ["XAI_API_KEY"] = settings.XAI_API_KEY

            if not base_model.startswith("xai/"):
                full_model_name = f"xai/{base_model}"
            else:
                full_model_name = base_model
            return full_model_name, kwargs

        # 6. Ollama / On-premise (OpenAI-compatible)
        if provider == "ollama":
            if settings.LLM_BASE_URL:
                kwargs["api_base"] = settings.LLM_BASE_URL

            if not base_model.startswith("ollama/"):
                full_model_name = f"ollama/{base_model}"
            else:
                full_model_name = base_model
            return full_model_name, kwargs

        raise ValueError(f"Unsupported LLM Provider: {provider}")

    async def ainvoke(self, input_data: Any) -> T | str:
        """
        Asynchronously invokes the LLM using LiteLLM.
        Returns instance of T if response_schema is set, otherwise returns string.
        """
        # 1. Process Input Data
        if hasattr(input_data, "to_string"):
            prompt_str = input_data.to_string()
        else:
            prompt_str = str(input_data)

        messages = [{"role": "user", "content": prompt_str}]

        # 2. LLM Call Settings
        call_kwargs = {
            "model": self.model_name,
            "messages": messages,
            **self.completion_kwargs,
        }

        # 3. Structured Output Settings
        if self.response_schema and settings.USE_STRUCTURED_OUTPUT:
            call_kwargs["response_format"] = self.response_schema

        # 4. LLM Call
        response = await litellm.acompletion(**call_kwargs)

        message = response.choices[0].message
        content = message.content or ""

        # 5. Parse LLM Response
        if self.response_schema:
            # Case A: LiteLLM already parsed into JSON (some providers supports Structured Output)
            if hasattr(message, "parsed") and message.parsed:
                return message.parsed  # type: ignore

            # Case B: Response in JSON string
            try:
                # If not using native structured output, model might return markdown json block
                if not settings.USE_STRUCTURED_OUTPUT:
                    content = self._extract_json(content)
                return self.response_schema.model_validate_json(content)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse structured output: {e}\nRaw Content: {content}"
                )

        return content

    def _extract_json(self, text: str) -> str:
        """Extracts JSON string from markdown code blocks if present."""
        import re

        json_match = re.search(r"```json\n?([\s\S]*?)\n?```", text)
        if json_match:
            return json_match.group(1).strip()
        return text.strip()

    def __call__(self):
        """Returns self to maintain compatibility with factory instantiation patterns."""
        return self
