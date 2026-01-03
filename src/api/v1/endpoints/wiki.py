"""src.api.v1.endpoints.wiki
FastAPI endpoints for managing wiki generation tasks and status.
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger

from src.models.api_schema import (
    TaskStatusResponse,
    WikiGenerationRequest,
    WikiGenerationResponse,
)
from src.services.task_store import create_task, get_task
from src.services.wiki_generator import WikiGenerationService
from src.services.wiki_worker import process_wiki_generation_task

router = APIRouter()


async def _init_wiki_generation(
    request: WikiGenerationRequest, initial_message: str
) -> tuple[str, Any, WikiGenerationService]:
    """Helper to initialize task and service for wiki generation."""
    try:
        WikiGenerationService.validate_request(request)
        task = create_task(initial_message=initial_message)
        service = WikiGenerationService(request)

        # Determine initial structure
        determiner = await service.prepare_generation()

        # Validate structure existence
        if not determiner.wiki_structure:
            raise ValueError("Failed to determine wiki structure.")

        return task.task_id, determiner, service

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to initialize wiki generation")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.post("/generate/file", response_model=WikiGenerationResponse)
async def generate_wiki_file(
    request: WikiGenerationRequest, background_tasks: BackgroundTasks
):
    """
    [Async] Generate Wiki & Save to Server

    - Triggers a background task to generate the wiki.
    - **Saves** the result as a Markdown file in the server's `output/` directory.
    - Returns a Task ID to track progress.
    """
    task_id, determiner, _ = await _init_wiki_generation(
        request, "Wiki structure determination started."
    )

    background_tasks.add_task(
        process_wiki_generation_task,
        task_id=task_id,
        request=request,
        determiner=determiner,
        save_file=True,
    )

    return WikiGenerationResponse(
        message="Wiki generation started in the background (File mode).",
        task_id=task_id,
        title=determiner.wiki_structure.title
        if determiner.wiki_structure
        else "Untitled",
        description=determiner.wiki_structure.description
        if determiner.wiki_structure
        else "",
    )


@router.post("/generate/text", response_model=WikiGenerationResponse)
async def generate_wiki_text(
    request: WikiGenerationRequest, background_tasks: BackgroundTasks
):
    """
    [Async] Generate Wiki & Return Text

    - Triggers a background task to generate the wiki.
    - **Does NOT save** to the server's filesystem.
    - The generated text will be available in the task status result.
    - Returns a Task ID to track progress.
    """
    task_id, determiner, _ = await _init_wiki_generation(
        request, "Wiki text generation started."
    )

    background_tasks.add_task(
        process_wiki_generation_task,
        task_id=task_id,
        request=request,
        determiner=determiner,
        save_file=False,
    )

    return WikiGenerationResponse(
        message="Wiki generation started in the background (Text mode).",
        task_id=task_id,
        title=determiner.wiki_structure.title
        if determiner.wiki_structure
        else "Untitled",
        description=determiner.wiki_structure.description
        if determiner.wiki_structure
        else "",
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_wiki_generation_status(task_id: str):
    """Retrieves the current status of a wiki generation task."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=404, detail=f"Task with ID {task_id} not found."
        )
    return task
