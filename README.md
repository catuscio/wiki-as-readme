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

> **Turn your codebase into a comprehensive Wiki in minutes, delivered in a single Readme.**

**Wiki As Readme** is an AI-powered tool that analyzes your Git repository (GitHub, GitLab, Bitbucket, or Local) and automatically generates a structured, detailed Wiki. It leverages modern LLMs (via **LiteLLM**) to understand your code structure, read your source files, and write professional-grade documentation, complete with Mermaid diagrams.

## ✨ Features

*   **🤖 Multi-LLM Support:**
    *   Powered by **LiteLLM**, supporting **Google Vertex AI (Gemini)**, **OpenAI (GPT-4)**, **Anthropic (Claude)**, **xAI (Grok)**, **Ollama**, and **OpenRouter**.
*   **🧠 Deep Context Analysis:**
    *   Analyzes file structure and relationships to understand the project's architecture before writing.
*   **📦 Smart Structure Generation:**
    *   Automatically determines a logical hierarchy (Sections > Pages) for your documentation.
*   **🔍 Comprehensive Content:**
    *   Writes detailed pages including architecture overviews, installation guides, and API references.
*   **📊 Automatic Diagrams:**
    *   Generates **Mermaid.js** diagrams (Flowcharts, Sequence diagrams, Class diagrams) to visualize architecture.
*   **🚉 Universal Repo Support:**
    *   Works with **GitHub**, **GitLab**, **Bitbucket**, and **Local File Systems**.
*   **🚗 Hybrid Output:**
    *   Generates both individual Markdown files for a Wiki and a single consolidated `README.md`.
*   **⚡ Async & Scalable:**
    *   Built with **FastAPI** and **AsyncIO** for non-blocking, efficient generation of large documentations.

## 🚀 Getting Started

### Prerequisites

*   **Python 3.12** or higher.
*   **[uv](https://github.com/astral-sh/uv)** (Recommended for dependency management).
*   **API Keys** for your chosen LLM Provider (e.g., Google Cloud Project, OpenAI API Key).

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/catuscio/wiki-as-readme.git
    cd wiki-as-readme
    ```

2.  **Install dependencies using `uv`**

    ```bash
    # Install uv if you haven't already
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Sync dependencies
    uv sync
    ```

3.  **Activate Virtual Environment**

    ```bash
    source .venv/bin/activate
    ```

### Configuration (`.env`)

This project uses a `.env` file for configuration, including LLM settings and API keys.

1.  **Copy the example file:**

    ```bash
    cp ".env example" .env
    ```

2.  **Edit `.env` and set the required variables:**

    | Category | Variable | Description | Example |
    | :--- | :--- | :--- | :--- |
    | **LLM Provider** | `LLM_PROVIDER` | Choose provider: `google`, `openai`, `anthropic`, `xai`, `openrouter`, `ollama` | `google` |
    | | `MODEL_NAME` | Specific model identifier | `gemini-2.0-flash-exp` or `gpt-4o` |
    | **Auth (Choose 1)** | `OPENAI_API_KEY` | For OpenAI provider | `sk-...` |
    | | `ANTHROPIC_API_KEY`| For Anthropic provider | `sk-ant-...` |
    | | `GCP_PROJECT_NAME` | **(Google Only)** Vertex AI Project ID | `my-genai-project` |
    | | `GCP_MODEL_LOCATION`| **(Google Only)** Region | `us-central1` |
    | **Advanced LLM** | `USE_STRUCTURED_OUTPUT`| Use native JSON mode (Requires model support) | `true` |
    | **Filtering** | `IGNORED_PATTERNS` | **JSON array** of glob patterns to exclude from analysis | `'["*.log", "node_modules/*"]'` |
    | **Git Access** | `GIT_API_TOKEN` | **Critical for private repos** and to avoid rate limits | `ghp_...` |
    | **App Config** | `API_BASE_URL` | URL for the backend API | `http://localhost:8000/api/v1` |
    | | `language` | Target language for the Wiki | `en`, `ko`, `ja` |

#### Detailed Settings

*   **`USE_STRUCTURED_OUTPUT`**:
    *   When set to `true`, the tool uses the LLM's native structured output capability (e.g., Gemini's JSON mode or OpenAI's Structured Outputs).
    *   This significantly improves the reliability of generated wiki structures and ensures consistent metadata.
    *   **Recommendation:** Keep `true` for modern models like Gemini 1.5 Pro/Flash, GPT-4o, or Claude 3.5 Sonnet.
*   **`IGNORED_PATTERNS`**:
    *   Allows you to exclude specific files or directories from being analyzed by the AI.
    *   **Crucial for token optimization**: Excluding large dependency folders (`node_modules`), build artifacts (`dist`, `build`), or lock files (`uv.lock`, `package-lock.json`) saves money and prevents the LLM from getting distracted.
    *   **Format**: Must be a single-line JSON array string (e.g., `'["*.png", "docs/*"]'`).

    > **Note for Google Vertex AI Users:**
    > You must authenticate your local environment using gcloud:
    > ```bash
    > gcloud auth application-default login
    > ```

## 💻 Usage

The application consists of two parts: the **FastAPI Backend** and the **Streamlit Frontend**. You need to run both.

### 1. Start the Backend API

Open a terminal and run:

```bash
uv run uvicorn src.server:app --reload --port 8000
```

### 2. Start the Streamlit UI

Open a **new** terminal window and run:

```bash
uv run streamlit run src/app.py
```

### 3. Generate Wiki

1.  Open your browser to the URL provided by Streamlit (usually `http://localhost:8501`).
2.  **Repo Information:** Enter your Repository URL (e.g., `https://github.com/owner/repo`) or Local Path.
3.  **Settings:** Toggle "Comprehensive View" or change language if needed.
4.  Click **✨ Generate Wiki**.
5.  Wait for the process to complete (it runs in the background).
6.  **Download:** Once finished, you can preview the content and download the consolidated `README.md`.

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

## 🐳 Docker Support

You can also run the API server using Docker Compose.

```bash
docker-compose up --build
```
*Note: This currently only starts the API server on port 8000. You will still need to run the Streamlit app locally or adapt the compose file.*

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
