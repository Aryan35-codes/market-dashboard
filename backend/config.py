import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Angel One SmartAPI Credentials
    ANGEL_API_KEY: str = os.getenv("ANGEL_API_KEY", "")
    ANGEL_CLIENT_ID: str = os.getenv("ANGEL_CLIENT_ID", "")
    ANGEL_PASSWORD: str = os.getenv("ANGEL_PASSWORD", "")
    ANGEL_TOTP_KEY: str = os.getenv("ANGEL_TOTP_KEY", "")

    # Cache TTLs (seconds)
    CACHE_TTL_OVERVIEW = 10
    CACHE_TTL_OPTIONS = 20
    CACHE_TTL_HEATMAP = 30
    CACHE_TTL_WATCHLIST = 30
    CACHE_TTL_MOOD = 60
    CACHE_TTL_NEWS = 60
    CACHE_TTL_SUMMARY = 180

    # Background refresh intervals (seconds)
    REFRESH_INTERVAL_FAST = 10      # overview
    REFRESH_INTERVAL_MEDIUM = 20    # options, heatmap
    REFRESH_INTERVAL_SLOW = 60      # news, mood, AI summary

    # Market hours (IST) - Mon-Fri, 9:15 AM to 3:30 PM
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 15
    MARKET_CLOSE_HOUR = 15
    MARKET_CLOSE_MINUTE = 30


settings = Settings()
