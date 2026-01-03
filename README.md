# 📚 Wiki As Readme

<p align="center">
  <img src="public/wiki-as-readme-banner.png" alt="Wiki as Readme Banner">
</p>

<p align="center">
  <a href="README_ko.md"><img src="https://img.shields.io/badge/Language-한국어-blue.svg" alt="한국어"></a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-orange?style=flat)](https://docs.litellm.ai/)

> **Turn your codebase into a comprehensive Wiki in minutes.**
>
> **Any Model. Any Repo. Any Environment.**

**Wiki As Readme** is the most flexible AI documentation tool available. Whether you're running a local Llama 3 model via Ollama, using Google's Gemini Pro, or hitting OpenAI's API, this tool adapts to your stack. It seamlessly integrates with any Git platform (GitHub, GitLab, Bitbucket) or local folders, making it the ultimate "drop-in" documentation solution.

> [!NOTE]
> Some features and integrations are currently under development. **Wiki-As-Readme** warmly welcomes your contributions and Pull Requests!

## ✨ Universal Compatibility

This project is built to be **truly pluggable**. You choose how to run it, where to run it, and what powers it.

### 🧠 1. Model Agnostic (Powered by LiteLLM)
*   **Commercial APIs:** Google Vertex AI (Gemini), OpenAI (GPT-4), Anthropic (Claude), xAI (Grok).
*   **Open/Local Models:** **Ollama**, OpenRouter, HuggingFace.
*   **On-Premise:** Connect to your own private LLM endpoints safely.

### 🚉 2. Platform Agnostic
*   **Cloud Repos:** Works seamlessly with **GitHub**, **GitLab**, and **Bitbucket**.
*   **Local Development:** Analyze code directly from your local file system without pushing.
*   **Private/Enterprise:** Full support for private instances and self-hosted Git servers.

### 🛠️ 3. Deployment Agnostic
*   **CI/CD:** Drop it into GitHub Actions.
*   **Container:** Run it via Docker Compose.
*   **Service:** Deploy as a long-running API server with Webhooks.
*   **CLI:** Run it locally while you code.

## ⚡ Core Features
*   **🧠 Deep Context Analysis:** Analyzes file structure and relationships to understand the project's architecture before writing.
*   **📦 Smart Structure Generation:** Automatically determines a logical hierarchy (Sections > Pages) for your documentation.
*   **🔍 Comprehensive Content:** Writes detailed pages including architecture overviews, installation guides, and API references.
*   **📊 Automatic Diagrams:** Generates **Mermaid.js** diagrams (Flowcharts, Sequence diagrams, Class diagrams) to visualize architecture.
*   **🚗 Hybrid Output:** Generates both individual Markdown files for a Wiki and a single consolidated `README.md`.
*   **⚡ Async & Scalable:** Built with **FastAPI** and **AsyncIO** for non-blocking, efficient generation of large documentations.

## 🚀 Usage Modes

This project is designed to be **pluggable** and can be used in multiple ways depending on your needs:

1.  **[GitHub Action](#1-github-action-recommended)**: Automate documentation updates in your CI/CD pipeline.
2.  **[Docker Compose (Local)](#2-docker-compose-local)**: Run the full UI/API locally without installing Python dependencies.
3.  **[Local Python Development](#3-local-python-development)**: For developers who want to modify the source code.
4.  **[Server & Webhooks](#4-server--webhooks)**: Deploy as a long-running service with Webhook support.

---

### 1. GitHub Action (Recommended)

Add this workflow to your repository to automatically update a `WIKI.md` file whenever you push changes.

1.  Create `.github/workflows/update-wiki.yml`:

    ```yaml
    name: Update Wiki README
    on:
      push:
        branches: [ main ]
        paths-ignore: ['WIKI.md', '.github/workflows/**']
      workflow_dispatch:

    permissions:
      contents: write

    jobs:
      generate-and-commit:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          
          - name: Generate Wiki
            uses: docker://ghcr.io/catuscio/wiki-as-readme-action:latest
            env:
              OUTPUT_FILE: "WIKI.md"
              LANGUAGE: "en" # or ko, ja
              LLM_PROVIDER: "google" # or openai, anthropic, etc.
              MODEL_NAME: "gemini-2.0-flash-exp"
              # Add your API keys as secrets to your repository
              GCP_PROJECT_NAME: ${{ secrets.GCP_PROJECT_NAME }}
              GCP_MODEL_LOCATION: ${{ secrets.GCP_MODEL_LOCATION }}
              GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}
              # OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

          - uses: stefanzweifel/git-auto-commit-action@v5
            with:
              commit_message: "docs: Update WIKI.md via Wiki-As-Readme"
              file_pattern: "WIKI.md"
    ```

### 2. Docker Compose (Local)

Run the application locally with a single command. This is the easiest way to try out the UI.

1.  **Configure `.env`**: 
    Copy `.env example` to `.env` and set your API keys (e.g., `LLM_PROVIDER`, `OPENAI_API_KEY` or `GCP_...`).

2.  **Run**:
    ```bash
    docker-compose up --build
    ```
3.  **Access**:
    *   **Web UI**: `http://localhost:8501`
    *   **API Docs**: `http://localhost:8000/docs`

### 3. Local Python Development

For developers who want to modify the source code or run without Docker.

**Prerequisites:** Python 3.12+, [uv](https://github.com/astral-sh/uv).

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/catuscio/wiki-as-readme.git
    cd wiki-as-readme
    uv sync
    source .venv/bin/activate
    ```

2.  **Configure `.env`**:
    Copy `.env example` to `.env` and set your variables.

3.  **Run Backend**:
    ```bash
    uv run uvicorn src.server:app --reload --port 8000
    ```

4.  **Run Frontend**:
    ```bash
    uv run streamlit run src/app.py
    ```

### 4. Server & Webhooks

You can deploy the API server to handle requests or webhooks (e.g., from GitHub).

*   **Endpoint**: `POST /api/v1/webhook/github`
*   **Payload**: Standard GitHub push event payload.
*   **Behavior**: Triggers a background task to generate the wiki for the repository and commit it back (requires `GIT_API_TOKEN`).

### Configuration Reference (`.env`)

Whether running locally or in Docker, you configure the app via environment variables:

| Category | Variable | Description | Example |
| :--- | :--- | :--- | :--- |
| **LLM Provider** | `LLM_PROVIDER` | `google`, `openai`, `anthropic`, `xai`, `openrouter`, `ollama` | `google` |
| | `MODEL_NAME` | Specific model identifier | `gemini-2.0-flash-exp` |
| **Auth** | `OPENAI_API_KEY` | OpenAI API Key | `sk-...` |
| | `GCP_PROJECT_NAME` | Vertex AI Project ID | `my-genai-project` |
| **Advanced** | `USE_STRUCTURED_OUTPUT`| Use native JSON mode | `true` |
| **Filtering** | `IGNORED_PATTERNS` | **JSON array** of glob patterns to exclude | `'["*.log", "node_modules/*"]'` |


## 🔌 API Reference

The backend API is built with FastAPI. You can access the interactive Swagger documentation at `http://localhost:8000/docs` when the server is running.

### Wiki Generation

#### `POST /api/v1/wiki/generate/file`
Starts a background task to generate the wiki and saves it as a Markdown file on the server.

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "repo_type": "github",
  "language": "en",
  "is_comprehensive_view": true
}
```

#### `POST /api/v1/wiki/generate/text`
Starts a background task to generate the wiki. The resulting text is stored in the task status.

#### `GET /api/v1/wiki/status/{task_id}`
Retrieves the status and result of a generation task.

### Webhooks

#### `POST /api/v1/webhook/github`
Endpoint for GitHub Webhooks (Push events). Triggers automatic wiki generation on pushes to the `main` branch.

## 📖 Examples

Curious about the results? Check out our sample outputs to see the quality of documentation generated by **Wiki As Readme**:

*   **[LangGraph Wiki Example (English)](examples/langgraph_readme_en.md)**: A high-quality, structured wiki generated from the [LangGraph](https://github.com/langchain-ai/langgraph) repository, featuring architecture overviews, core concepts, and Mermaid diagrams.
*   **[LangGraph Wiki Example (Korean)](examples/langgraph_readme_ko.md)**: The same LangGraph wiki, but generated in Korean.
*   **[Wiki As Readme's Own Wiki](examples/wiki_as_README.md)**: Documentation for this project, generated by itself!


## 🛠️ Architecture

*   **Frontend:** [Streamlit](https://streamlit.io/) (User Interface)
*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (REST API, Background Tasks)
*   **LLM Integration:** [LiteLLM](https://docs.litellm.ai/) (Unified interface for 100+ LLMs)
*   **Data Models:** [Pydantic](https://docs.pydantic.dev/) (Type safety & Structured Output validation)
*   **Diagrams:** Mermaid.js

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

-----

### Acknowledgments

*   This project is heavily influenced by and utilizes core logic from [deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open).
*   Built with the power of open-source libraries.
*   Inspired by the need for better automated documentation.
