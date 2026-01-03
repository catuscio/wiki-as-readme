"""src.services.wiki_worker
Background worker task handler for asynchronous wiki generation.
"""

from loguru import logger

from src.models.api_schema import WikiGenerationRequest
from src.services.structure_analyzer import WikiStructureDeterminer
from src.services.task_store import update_task_status
from src.services.wiki_generator import WikiGenerationService


async def process_wiki_generation_task(
    task_id: str,
    request: WikiGenerationRequest,
    determiner: WikiStructureDeterminer | None = None,  # If None, start from scratch
    save_file: bool = False,
):
    """
    Unified background task handler.
    """
    service = WikiGenerationService(request)

    try:
        # 1. Wiki generation (text)
        markdown_content = await service.generate_wiki(determiner)

        result = {"markdown_content": markdown_content}

        # 2. Save file (optional)
        if save_file:
            file_path = await service.save_to_file(markdown_content)
            result["file_path"] = file_path

        # 3. Update task status to completed
        update_task_status(task_id, "completed", result)

    except Exception as e:
        logger.exception(f"Task {task_id} failed")
        update_task_status(task_id, "failed", {"error": str(e)})

    finally:
        # If a determiner was injected from outside, it's safer to close it here
        if determiner:
            await determiner.close()
