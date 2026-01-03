"""src.server
FastAPI server entry point for Wiki As Readme API.
"""

from src.core.logger_config import setup_logging

setup_logging()

import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.api.v1.endpoints import webhook, wiki

app = FastAPI(
    title="Wiki as Readme",
    description="Turn your codebase into a comprehensive Wiki in minutes, delivered in a single Readme.",
    version="1.0.0",
)


@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok"}


# Include the API routers
app.include_router(wiki.router, prefix="/api/v1/wiki", tags=["Wiki Generation"])
app.include_router(
    webhook.router, prefix="/api/v1/webhook", tags=["Webhook Integration"]
)

if __name__ == "__main__":
    logger.info("Starting Wiki As Readme API server...")
    # The default host "127.0.0.1" is used. To expose it, use host="0.0.0.0".
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
