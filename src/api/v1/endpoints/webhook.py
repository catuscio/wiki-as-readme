import base64
import hashlib
import hmac
import logging
import os

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from src.models.api_schema import WikiGenerationRequest
from src.models.github_webhook_schema import GitHubPushPayload

# Logging configuration
logger = logging.getLogger("webhook")
router = APIRouter()

# Environment variable configuration
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_ACCESS_TOKEN = os.getenv(
    "GITHUB_ACCESS_TOKEN"
)  # Token to write files to GitHub (PAT)

# Bot committer name or email to ignore its own commits (prevents infinite loops)
BOT_COMMITTER_NAME = "Wiki-As-Readme-Bot"


async def verify_signature(request: Request):
    """HMAC signature verification"""
    if not GITHUB_WEBHOOK_SECRET:
        return
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=403, detail="Signature missing")
    body = await request.body()
    hash_object = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"), msg=body, digestmod=hashlib.sha256
    )
    if not hmac.compare_digest(f"sha256={hash_object.hexdigest()}", signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature")


async def update_github_readme(repo_owner: str, repo_name: str, content: str):
    """
    [Core Feature] Commits the generated markdown content to GitHub's README.md (or WIKI.md).
    """
    if not GITHUB_ACCESS_TOKEN:
        logger.error("GITHUB_ACCESS_TOKEN is missing. Cannot update WIKI.")
        return

    api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/WIKI.md"
    headers = {
        "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient() as client:
        # 1. Get SHA of existing README.md (required for overwriting)
        get_resp = await client.get(api_base, headers=headers)
        sha = None
        if get_resp.status_code == 200:
            sha = get_resp.json().get("sha")

        # 2. Base64 encode content (GitHub API requirement)
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        # 3. Configure commit data
        commit_data = {
            "message": "docs: Update README.md via Wiki-As-Readme",  # Commit message
            "content": encoded_content,
            "committer": {
                "name": BOT_COMMITTER_NAME,
                "email": "bot@wiki-as-readme.com",
            },
        }
        if sha:
            commit_data["sha"] = sha

        # 4. Update file (PUT)
        put_resp = await client.put(api_base, json=commit_data, headers=headers)

        if put_resp.status_code in [200, 201]:
            logger.info(f"Successfully updated README.md for {repo_owner}/{repo_name}")
        else:
            logger.error(f"Failed to update GitHub: {put_resp.text}")


async def process_full_cycle(
    generate_url: str, request_data_json: str, repo_owner: str, repo_name: str
):
    """
    Full process: Wiki Generation -> Get Result -> Upload to GitHub
    """
    try:
        # 1. Call internal Wiki generation API
        async with httpx.AsyncClient() as client:
            # Timeout 60s (considering generation time)
            gen_resp = await client.post(
                generate_url,
                json=request_data_json,  # request_data_json is already a string, so data= or json parsing is needed
                # Since it's passed as a string here, it needs to be handled via data/content,
                # but httpx json parameter expects a dict, so we convert it or send as content.
                headers={"Content-Type": "application/json"},
                timeout=60.0,
            )
            gen_resp.raise_for_status()

            # 2. Extract generated result (Markdown)
            # Assumption: Generation API returns {"result": "# Generated Markdown..."}
            generated_markdown = gen_resp.json().get("result")

            if not generated_markdown:
                logger.warning("Generation API returned empty result.")
                return

        # 3. Upload to GitHub
        await update_github_readme(repo_owner, repo_name, generated_markdown)

    except Exception as e:
        logger.error(f"Error in background task: {str(e)}")


@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    payload: GitHubPushPayload, request: Request, background_tasks: BackgroundTasks
):
    await verify_signature(request)

    # [Important] Prevent infinite loops: ignore commits made by the bot
    pusher_name = payload.pusher.name if payload.pusher else ""
    head_commit_msg = payload.head_commit.message if payload.head_commit else ""

    # Filter by bot name or commit message
    if pusher_name == BOT_COMMITTER_NAME or "via Wiki-As-Readme" in head_commit_msg:
        return {"message": "Skipping my own commit."}

    if payload.ref != "refs/heads/main":
        return {"message": "Ignored non-main branch"}

    repo_owner = payload.repository.owner.login
    repo_name = payload.repository.name

    internal_request_data = WikiGenerationRequest(
        repo_type="github",
        repo_owner=repo_owner,
        repo_name=repo_name,
        repo_url=f"https://github.com/{repo_owner}/{repo_name}",
        language="ko",
        is_comprehensive_view=True,
    )

    base_url = str(request.base_url)
    generate_url = f"{base_url}api/v1/wiki/generate/file"

    # Start Background task (Generation -> Push)
    background_tasks.add_task(
        process_full_cycle,
        generate_url,
        internal_request_data.model_dump_json(),
        repo_owner,
        repo_name,
    )

    return {"message": "Processing started: Generate & Update README."}
