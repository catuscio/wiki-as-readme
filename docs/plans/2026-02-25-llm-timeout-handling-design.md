# LLM Timeout Handling Design

## Problem

LLM calls can fail with timeout errors (observed: 600s default timeout in LiteLLM).
When a page fails, the raw error string is stored and included in the final wiki output.

## Approach

Enhance LiteLLM's built-in retry by explicitly setting timeout, and improve error placeholders.

## Changes

### 1. `src/core/config.py`
- Add `llm_timeout: int = 300` (5 min, configurable via `LLM_TIMEOUT` env var)

### 2. `src/agent/llm.py`
- Pass `timeout` to `litellm.acompletion()` kwargs

### 3. `src/services/structure_analyzer.py`
- Replace raw error string with user-friendly markdown placeholder
- Bilingual support (en/ko) based on language setting

## Error Placeholder Format

```markdown
> **Content generation failed for this section.**
>
> Cause: {error_message}
>
> Re-running the workflow may resolve this issue.
```
