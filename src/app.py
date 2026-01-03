"""src.app
Streamlit demo application for AI Wiki Generator.
"""

import asyncio
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


# --- API Interaction ---
async def start_generation_task(request_data: WikiGenerationRequest) -> str | None:
    """
    Starts the wiki generation task and returns the task ID.
    """
    start_url = f"{API_BASE_URL}/wiki/generate/text"
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
    Returns the result dict if completed, None if failed (handled internally),
    or loops forever updating UI until done/interrupted.
    """
    status_url = f"{API_BASE_URL}/wiki/status/{task_id}"

    status_placeholder = st.empty()
    progress_bar = st.progress(0, text="Resuming task...")

    # We don't have the original start time across reruns easily without persisting it,
    # but a relative elapsed time for this polling session is okay.
    # Optionally, we could save start_time in session_state too.
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
                    # Transient network error, wait and retry
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
                    # Return a special flag or just None to indicate failure/stop
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


# --- UI Components ---
def render_sidebar() -> WikiGenerationRequest | None:
    """
    Renders the sidebar and returns the configuration if the 'Generate' button is clicked.
    """
    with st.sidebar:
        st.header("Repo Information")

        # Initialize session state for persistent inputs
        if "saved_repo_input" not in st.session_state:
            st.session_state.saved_repo_input = ""

        # Callbacks to sync widget state to persistent state
        def save_repo_input():
            st.session_state.saved_repo_input = st.session_state.widget_repo_input

        # Unified Input Field
        repo_input = st.text_input(
            "Repository URL or Local Path",
            value=st.session_state.saved_repo_input,
            placeholder="https://github.com/owner/repo OR /path/to/repo",
            key="widget_repo_input",
            on_change=save_repo_input,
            help="Enter a GitHub/GitLab URL or a local folder path.",
        )
        # Ensure persistence
        st.session_state.saved_repo_input = repo_input

        st.header("Generation Settings")

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

        # Google Cloud Note
        st.info("**Note:** Setup `.env` first")

        submitted = st.button(
            "✨ Generate Wiki",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            # Automatic Detection Logic
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
                # Create and validate request object
                return WikiGenerationRequest(
                    repo_type=repo_type_value,
                    repo_url=repo_url,
                    local_path=local_path,
                    language=language,
                    is_comprehensive_view=is_comprehensive,
                )
            except ValidationError as e:
                # Display friendly validation errors
                for error in e.errors():
                    field = error["loc"][0]
                    msg = error["msg"]
                    st.error(f"Invalid {field}: {msg}")
                return None

    return None


def render_main_content(result: dict[str, Any] | None):
    """
    Renders the main content area with the generation results.
    """
    if result and "markdown_content" in result:
        st.success("Wiki generation complete!")

        markdown_content = result["markdown_content"]

        st.download_button(
            label="📥 Download Consolidated Wiki (README.md)",
            data=markdown_content,
            file_name="README.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.markdown("### Preview")

        # Split markdown by mermaid blocks and render them
        # Regex to find ```mermaid ... ``` blocks
        parts = re.split(r"(```mermaid\s+.*?\s+```)", markdown_content, flags=re.DOTALL)

        for part in parts:
            if part.startswith("```mermaid"):
                # Extract the code between the fences
                mermaid_code = re.search(r"```mermaid\s+(.*?)\s+```", part, re.DOTALL)
                if mermaid_code:
                    st_mermaid(mermaid_code.group(1).strip())
            else:
                # Regular markdown text
                st.markdown(part, unsafe_allow_html=True)

    elif result and "error" in result:
        # Error handled in poll, but if passed here:
        st.error(f"Generation failed: {result['error']}")
    elif result:
        st.error(f"Unexpected API response format: {result}")


# --- Main Application ---
def main():
    st.set_page_config(page_title="Wiki As Readme", page_icon="📕", layout="wide")

    st.title("Wiki As Readme")
    st.caption(
        "Generate comprehensive documentation for your code repositories using AI."
    )

    # Initialize State
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False
    if "task_id" not in st.session_state:
        st.session_state.task_id = None
    if "generation_result" not in st.session_state:
        st.session_state.generation_result = None

    # Render sidebar and get request object if submitted
    request_data = render_sidebar()

    # Case 1: Start new generation
    if request_data:
        task_id = asyncio.run(start_generation_task(request_data))
        if task_id:
            st.session_state.task_id = task_id
            st.session_state.is_generating = True
            st.session_state.generation_result = None
            st.session_state.task_start_time = time.time()
            st.rerun()

    # Case 2: Continue generation (Polling)
    if st.session_state.is_generating and st.session_state.task_id:
        result = asyncio.run(poll_task_status(st.session_state.task_id))

        # If we got a result (success or failure dict), stop generating
        if result:
            st.session_state.is_generating = False
            st.session_state.generation_result = result
            st.rerun()
        # If result is None, it means polling was interrupted (e.g. tab switch)
        # or still waiting. On next rerun, we re-enter this block.

    # Case 3: Display Result
    if st.session_state.generation_result:
        render_main_content(st.session_state.generation_result)

    # Initial state hint
    if not st.session_state.is_generating and not st.session_state.generation_result:
        st.info(
            "👈 Enter repository details in the sidebar and click 'Generate Wiki' to start."
        )


if __name__ == "__main__":
    main()
