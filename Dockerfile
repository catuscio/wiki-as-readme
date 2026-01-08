# Stage 1: Builder
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

# Install all dependencies (api + ui)
RUN uv sync --frozen --no-dev --no-install-project --extra all

# Stage 2: Final Image
FROM python:3.12-slim-bookworm

LABEL maintainer="catuscio <catuscio@hotmail.com>"
LABEL description="Full application for wiki-as-readme (API + UI)"
LABEL org.opencontainers.image.source="https://github.com/catuscio/wiki-as-readme"
LABEL org.opencontainers.image.description="Turn your codebase into a comprehensive Wiki in minutes"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="catuscio <catuscio@hotmail.com>"
LABEL org.opencontainers.image.title="wiki-as-readme"
LABEL org.opencontainers.image.version="1.2.3"

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY src ./src
COPY entrypoint.sh .

RUN chown -R appuser:appuser /app && \
    chmod +x entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Expose API and Streamlit ports
EXPOSE 8000
EXPOSE 8501

USER appuser

CMD ["./entrypoint.sh"]
