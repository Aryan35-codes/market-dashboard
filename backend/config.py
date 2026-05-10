import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Cache TTLs (seconds)
    CACHE_TTL_OVERVIEW = 15
    CACHE_TTL_OPTIONS = 25
    CACHE_TTL_HEATMAP = 30
    CACHE_TTL_WATCHLIST = 30
    CACHE_TTL_MOOD = 60
    CACHE_TTL_NEWS = 120
    CACHE_TTL_SUMMARY = 180

    # Background refresh intervals (seconds)
    REFRESH_INTERVAL_FAST = 15      # overview, options
    REFRESH_INTERVAL_MEDIUM = 30    # heatmap, watchlist
    REFRESH_INTERVAL_SLOW = 120     # news, AI summary

    # Market hours (IST) - Mon-Fri, 9:15 AM to 3:30 PM
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 15
    MARKET_CLOSE_HOUR = 15
    MARKET_CLOSE_MINUTE = 30


settings = Settings()
