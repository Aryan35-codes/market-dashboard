"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from scheduler import start_background_tasks
from routes.market import router
from services.nse_service import nse

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
    logger.info("Starting Market Intelligence Backend...")
    tasks = await start_background_tasks()
    yield
    logger.info("Shutting down...")
    for task in tasks:
        task.cancel()
    await nse.close()


app = FastAPI(
    title="Market Intelligence API",
    description="Compressed market data for fast consumption",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For easier initial deployment, allowing all. Change to specific domains in production.
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/market", tags=["market"])
