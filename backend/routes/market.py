"""API routes — all endpoints read from cache. No upstream calls happen here."""

from fastapi import APIRouter
from cache import cache

router = APIRouter()


def _cached_response(key: str) -> dict:
    """Return cached data with age metadata, or a loading state."""
    result = cache.get(key)
    if result:
        data, stored_at = result
        age = cache.get_age_seconds(key)
        return {
            "status": "ok",
            "data": data,
            "cache_age_seconds": age,
        }
    return {
        "status": "loading",
        "data": None,
        "cache_age_seconds": None,
        "message": "Data is being loaded. Please retry in a few seconds.",
    }


@router.get("/overview")
async def get_overview():
    return _cached_response("market_overview")


@router.get("/summary")
async def get_summary():
    return _cached_response("ai_summary")


@router.get("/watchlist")
async def get_watchlist():
    return _cached_response("smart_watchlist")


@router.get("/options")
async def get_options():
    return _cached_response("options_snapshot")


@router.get("/news")
async def get_news():
    return _cached_response("market_news")


@router.get("/heatmap")
async def get_heatmap():
    return _cached_response("sector_heatmap")


@router.get("/mood")
async def get_mood():
    return _cached_response("market_mood")


@router.get("/health")
async def health():
    return {"status": "ok"}
