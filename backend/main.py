"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from scheduler import start_background_tasks
from routes.market import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: launch background tasks. Shutdown: cleanup."""
    logger.info("Starting GyanDheesh Backend...")
    tasks = await start_background_tasks()
    yield
    logger.info("Shutting down...")
    for task in tasks:
        task.cancel()


app = FastAPI(
    title="GyanDheesh API",
    description="Compressed market intelligence for fast consumption",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "https://*.vercel.app"
    ],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/market", tags=["market"])
