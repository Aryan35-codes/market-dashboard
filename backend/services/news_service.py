"""RSS feed parser for market news from Moneycontrol, ET Markets, and Mint."""

import feedparser
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from normalizer.normalize import normalize_news_item, ts_now

logger = logging.getLogger(__name__)

FEEDS = {
    "Moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
    "ET Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Livemint": "https://www.livemint.com/rss/markets",
}

# Keywords to classify news into sectors
SECTOR_KEYWORDS = {
    "Banking": ["bank", "npa", "rbi", "credit", "loan", "nbfc", "hdfc", "icici", "sbi", "kotak", "axis"],
    "IT": ["it ", "tech", "infosys", "tcs", "wipro", "hcl", "software", "digital", "saas"],
    "Auto": ["auto", "car", "vehicle", "maruti", "tata motors", "ev ", "electric vehicle", "mahindra"],
    "Pharma": ["pharma", "drug", "health", "hospital", "cipla", "sun pharma", "biocon", "fda"],
    "Energy": ["oil", "gas", "ongc", "reliance", "petrol", "diesel", "energy", "power", "coal", "adani green"],
    "Metals": ["metal", "steel", "aluminium", "copper", "tata steel", "hindalco", "vedanta", "mining"],
    "FMCG": ["fmcg", "consumer", "itc ", "hul ", "nestle", "britannia", "dabur", "godrej"],
    "Realty": ["real estate", "realty", "housing", "dlf", "godrej properties", "oberoi"],
    "Global Markets": ["us market", "nasdaq", "dow", "s&p", "fed ", "wall street", "global", "china", "europe", "asia", "ftse", "nikkei"],
}

_executor = ThreadPoolExecutor(max_workers=3)


def _parse_single_feed(source: str, url: str) -> list[dict]:
    """Parse a single RSS feed (sync, runs in thread pool)."""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            # Strip HTML tags from summary
            import re
            summary = re.sub(r"<[^>]+>", "", summary)

            items.append(
                normalize_news_item(
                    title=title,
                    summary=summary,
                    source=source,
                    url=entry.get("link", ""),
                    published=entry.get("published", ""),
                ).model_dump()
            )
        return items
    except Exception as e:
        logger.error(f"Feed parse error for {source}: {e}")
        return []


def _classify_sector(text: str) -> str:
    """Classify a news item into a sector based on keyword matching."""
    text_lower = text.lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return sector
    return "General"


async def fetch_market_news() -> dict:
    """Fetch and categorize news from all RSS feeds."""
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(_executor, _parse_single_feed, source, url)
        for source, url in FEEDS.items()
    ]
    results = await asyncio.gather(*tasks)

    # Flatten and classify
    all_news = []
    for feed_items in results:
        all_news.extend(feed_items)

    # Classify into sectors
    sectors: dict[str, list] = {}
    for item in all_news:
        sector = _classify_sector(item["title"] + " " + item["summary"])
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(item)

    # Keep top 5 per sector
    for sector in sectors:
        sectors[sector] = sectors[sector][:5]

    return {
        "sectors": sectors,
        "updated_at": ts_now(),
    }
