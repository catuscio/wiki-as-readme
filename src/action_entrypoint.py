"""
action_entrypoint.py
GitHub Action entrypoint for generating repository documentation (Wiki/README) using AI.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import src modules
sys.path.append(os.getcwd())

from loguru import logger

from src.models.api_schema import WikiGenerationRequest
from src.services.wiki_generator import WikiGenerationService


async def main():
    """
    Entrypoint for GitHub Action to generate Wiki/README.
    """
    # 1. Inputs from Environment Variables
    local_path = os.getenv("INPUT_LOCAL_PATH", ".")
    output_file = (
        os.getenv("OUTPUT_FILE") or os.getenv("INPUT_OUTPUT_FILE") or "WIKI.md"
    )
    language = os.getenv("LANGUAGE") or os.getenv("INPUT_LANGUAGE") or "ko"

    # Optional: Log the configuration (be careful not to log secrets)
    logger.info("Action triggered with:")
    logger.info(f"  Local Path: {local_path}")
    logger.info(f"  Output File: {output_file}")
    logger.info(f"  Language: {language}")

    # 2. Construct Request
    # We use repo_type="local" because the Action checks out the code locally.
    request = WikiGenerationRequest(
        repo_type="local",
        local_path=local_path,
        repo_owner="action",  # Placeholder
        repo_name="action",  # Placeholder
        language=language,
        is_comprehensive_view=True,
    )

    # 3. Initialize Service and Generate
    service = WikiGenerationService(request)
    try:
        logger.info("Starting Wiki Generation...")
        markdown = await service.generate_wiki()

        if not markdown:
            logger.error("Generated content is empty.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        # Print full traceback for debugging in Actions logs
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # 4. Write Output
    output_path = Path(local_path) / output_file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        logger.info(f"Successfully wrote wiki to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
