"""src.app
Streamlit demo application for AI Wiki Generator.
"""

import asyncio
import glob
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx
import streamlit as st
from pydantic import ValidationError
from streamlit_mermaid import st_mermaid

# Add project root to sys.path to allow absolute imports from 'src'
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.models.api_schema import WikiGenerationRequest

# --- Configuration ---
# Default to localhost:8000 but allow override via environment variable
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
OUTPUT_DIR = "output"  # Directory where wiki files are saved


# --- API Interaction ---
async def start_generation_task(request_data: WikiGenerationRequest) -> str | None:
    """
    Starts the wiki generation task and returns the task ID.
    Uses /wiki/generate/file endpoint to save the result on the server.
    """
    start_url = f"{API_BASE_URL}/wiki/generate/file"
    payload = request_data.model_dump(exclude_none=True, mode="json")

    try:
        async with httpx.AsyncClient() as client:
            st.toast("🚀 Requesting wiki generation...")
            response = await client.post(start_url, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("task_id")
    except httpx.HTTPStatusError as e:
        st.error(f"API Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError:
        st.error(
            f"Network Error: Could not connect to {API_BASE_URL}. Is the server running?"
        )
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return None


async def poll_task_status(task_id: str) -> dict[str, Any] | None:
    """
    Polls the status of the task.
    Returns the result dict if completed, None if failed.
    """
    status_url = f"{API_BASE_URL}/wiki/status/{task_id}"

    status_placeholder = st.empty()
    progress_bar = st.progress(0, text="Resuming task...")

    if "task_start_time" not in st.session_state:
        st.session_state.task_start_time = time.time()

    start_time = st.session_state.task_start_time

    try:
        async with httpx.AsyncClient() as client:
            while True:
                elapsed = int(time.time() - start_time)

                try:
                    status_response = await client.get(status_url, timeout=10.0)
                    status_response.raise_for_status()
                    status_data = status_response.json()
                except httpx.RequestError:
                    await asyncio.sleep(2.0)
                    continue

                status = status_data.get("status")
                result = status_data.get("result")

                if status == "completed":
                    progress_bar.progress(100, text="Done!")
                    time.sleep(0.5)
                    status_placeholder.empty()
                    progress_bar.empty()
                    return result

                if status == "failed":
                    error_msg = (
                        result.get("error", "Unknown error")
                        if result
                        else "Unknown error"
                    )
                    st.error(f"Task failed: {error_msg}")
                    status_placeholder.empty()
                    progress_bar.empty()
                    return {"error": error_msg}

                # In progress
                status_placeholder.markdown(
                    f"⏳ **Generating...** (Elapsed: {elapsed}s)"
                )
                fake_progress = min(90, int(elapsed * 1.5))
                progress_bar.progress(fake_progress, text=f"Processing... ({elapsed}s)")

                await asyncio.sleep(2.0)

    except Exception as e:
        st.error(f"Polling error: {e}")
        return None


# --- Helper Functions ---
def get_generated_files() -> list[str]:
    """Returns a list of generated markdown files in the output directory."""
    if not os.path.exists(OUTPUT_DIR):
        return []
    # Sort by modification time (newest first)
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.md"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def render_markdown_with_mermaid(markdown_content: str):
    """Renders markdown content, handling Mermaid diagrams separately."""
    parts = re.split(r"(```mermaid\s+.*?\s+```)", markdown_content, flags=re.DOTALL)

    for part in parts:
        if part.startswith("```mermaid"):
            mermaid_code = re.search(r"```mermaid\s+(.*?)\s+```", part, re.DOTALL)
            if mermaid_code:
                st_mermaid(mermaid_code.group(1).strip())
        else:
            st.markdown(part, unsafe_allow_html=True)


# --- Pages ---
def render_generator_page():
    """Renders the main Generator page."""
    st.header("Repo Information")

    # Sidebar Inputs
    with st.sidebar:
        st.header("Configuration")

        # Initialize session state for persistent inputs
        if "saved_repo_input" not in st.session_state:
            st.session_state.saved_repo_input = ""

        def save_repo_input():
            st.session_state.saved_repo_input = st.session_state.widget_repo_input

        repo_input = st.text_input(
            "Repository URL or Local Path",
            value=st.session_state.saved_repo_input,
            placeholder="https://github.com/owner/repo OR /path/to/repo",
            key="widget_repo_input",
            on_change=save_repo_input,
            help="Enter a GitHub/GitLab URL or a local folder path.",
        )
        st.session_state.saved_repo_input = repo_input

        is_comprehensive = st.toggle(
            "Comprehensive View",
            value=True,
            help="Generate a more detailed and structured wiki with more pages.",
            key="is_comprehensive",
        )
        language = st.selectbox(
            "Language",
            options=["ko", "en", "ja", "zh"],
            index=0,
            help="Select the language for the generated wiki.",
            key="language",
        )

        st.divider()
        st.info("💡 **Note:** Setup `.env` first")
        st.info(
            "🐳 **Docker Tip:** For local analysis, use paths starting with `/app/target_repo` "
            "(e.g., `/app/target_repo/your-project`)"
        )

        submitted = st.button(
            "✨ Generate Wiki", type="primary", use_container_width=True
        )

    # Logic for Generation Request
    request_data = None
    if submitted:
        repo_type_value = "local"
        repo_url = None
        local_path = None
        clean_input = repo_input.strip()

        if clean_input.startswith(("http://", "https://", "git@")):
            repo_url = clean_input
            if "gitlab" in clean_input:
                repo_type_value = "gitlab"
            elif "bitbucket" in clean_input:
                repo_type_value = "bitbucket"
            else:
                repo_type_value = "github"
        else:
            repo_type_value = "local"
            local_path = clean_input

        try:
            request_data = WikiGenerationRequest(
                repo_type=repo_type_value,
                repo_url=repo_url,
                local_path=local_path,
                language=language,
                is_comprehensive_view=is_comprehensive,
            )
        except ValidationError as e:
            for error in e.errors():
                st.error(f"Invalid {error['loc'][0]}: {error['msg']}")

    # Start Task
    if request_data:
        task_id = asyncio.run(start_generation_task(request_data))
        if task_id:
            st.session_state.task_id = task_id
            st.session_state.is_generating = True
            st.session_state.generation_result = None
            st.session_state.task_start_time = time.time()
            st.rerun()

    # Poll Status
    if st.session_state.is_generating and st.session_state.task_id:
        result = asyncio.run(poll_task_status(st.session_state.task_id))
        if result:
            st.session_state.is_generating = False
            st.session_state.generation_result = result
            st.rerun()

    # Display Result
    if st.session_state.generation_result:
        result = st.session_state.generation_result
        if "markdown_content" in result:
            st.success("Wiki generation complete!")

            # Use file_path from result if available, otherwise default name
            file_name = "README.md"
            if "file_path" in result:
                file_name = os.path.basename(result["file_path"])

            st.download_button(
                label=f"📥 Download {file_name}",
                data=result["markdown_content"],
                file_name=file_name,
                mime="text/markdown",
                use_container_width=True,
            )

            st.markdown("### Preview")
            render_markdown_with_mermaid(result["markdown_content"])

        elif "error" in result:
            st.error(f"Generation failed: {result['error']}")

    # Initial Hint
    if not st.session_state.is_generating and not st.session_state.generation_result:
        st.info(
            "👈 Enter repository details in the sidebar and click 'Generate Wiki' to start."
        )


def render_history_page():
    """Renders the History page listing generated files in a grid layout."""
    import datetime

    st.header("📚 Generated Wikis (History)")
    st.caption(f"Files located in: `{os.path.abspath(OUTPUT_DIR)}`")

    files = get_generated_files()

    if not files:
        st.warning("No generated wiki files found yet.")
        return

    # Initialize selection state
    if "history_selected_file" not in st.session_state:
        st.session_state.history_selected_file = None

    # Grid Layout
    cols = st.columns(3)
    for idx, file_path in enumerate(files):
        file_name = os.path.basename(file_path)
        stats = os.stat(file_path)
        # Format date: YYYY-MM-DD HH:MM
        mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime(
            "%Y-%m-%d %H:%M"
        )
        file_size_kb = stats.st_size / 1024

        with cols[idx % 3], st.container(border=True):
            st.markdown(f"**📄 {file_name}**")
            st.caption(f"📅 {mod_time} | 💾 {file_size_kb:.1f} KB")

            # Action Buttons
            c1, c2 = st.columns(2)
            with c1:
                if st.button(
                    "👁️ View",
                    key=f"view_{file_name}",
                    use_container_width=True,
                ):
                    st.session_state.history_selected_file = file_path
                    st.rerun()
            with c2, open(file_path, "rb") as f:
                st.download_button(
                    label="📥 Save",
                    data=f,
                    file_name=file_name,
                    mime="text/markdown",
                    key=f"dl_{file_name}",
                    use_container_width=True,
                )

    st.divider()

    # Preview Section
    if st.session_state.history_selected_file:
        selected_path = st.session_state.history_selected_file
        if os.path.exists(selected_path):
            st.subheader(f"📖 Preview: {os.path.basename(selected_path)}")
            try:
                with open(selected_path, encoding="utf-8") as f:
                    content = f.read()
                render_markdown_with_mermaid(content)
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            st.error("File not found. It might have been deleted.")


# --- Main Application ---
def main():
    st.set_page_config(page_title="Wiki As Readme", page_icon="📕", layout="wide")
    st.title("Wiki As Readme")

    # Initialize State
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False
    if "task_id" not in st.session_state:
        st.session_state.task_id = None
    if "generation_result" not in st.session_state:
        st.session_state.generation_result = None

    # Navigation
    page = st.sidebar.radio("Navigation", ["Generator", "History"], index=0)

    if page == "Generator":
        render_generator_page()
    elif page == "History":
        render_history_page()


if __name__ == "__main__":
    main()
