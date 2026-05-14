"""AI summarization service using Google Gemini Flash via the new google-genai SDK.

Follows the structured signal extraction pattern:
  Raw data → structured signals → AI converts to readable summary.
AI is used ONLY for summarization, never for prediction.
"""

import json
import logging
from google import genai
from config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-flash-latest"


def extract_structured_signals(
    overview: dict | None,
    heatmap: dict | None,
    news: dict | None,
    options: dict | None,
    mood: dict | None,
) -> dict:
    """Extract structured signals from normalized market data.
    This is the intermediate step BEFORE sending to AI."""

    signals = {
        "global_sentiment": "neutral",
        "strong_sectors": [],
        "weak_sectors": [],
        "important_events": [],
        "volatility": "moderate",
        "market_breadth": None,
        "key_levels": None,
    }

    # Derive sentiment from indices
    if overview and overview.get("indices"):
        ups = sum(1 for i in overview["indices"] if i.get("direction") == "up")
        total = len(overview["indices"])
        if ups > total * 0.65:
            signals["global_sentiment"] = "positive"
        elif ups < total * 0.35:
            signals["global_sentiment"] = "negative"
        else:
            signals["global_sentiment"] = "mixed"

    # Derive sector strength from heatmap
    if heatmap and heatmap.get("sectors"):
        for s in heatmap["sectors"]:
            pct = s.get("change_percent", 0)
            name = s.get("name", "")
            if pct > 0.5:
                signals["strong_sectors"].append(f"{name} (+{pct}%)")
            elif pct < -0.5:
                signals["weak_sectors"].append(f"{name} ({pct}%)")

    # Extract top news headlines as events
    if news and news.get("sectors"):
        events = []
        for sector, items in news["sectors"].items():
            for item in items[:2]:
                events.append(item.get("title", ""))
        signals["important_events"] = events[:10]

    # Options-derived levels
    if options:
        pcr = options.get("pcr", 0)
        if pcr > 1.2:
            signals["volatility"] = "high (protective puts elevated)"
        elif pcr < 0.7:
            signals["volatility"] = "low (bullish bias)"
        signals["key_levels"] = {
            "max_pain": options.get("max_pain"),
            "pcr": pcr,
        }

    return signals


async def generate_market_summary(signals: dict) -> str:
    """Use Gemini Flash to convert structured signals into a readable 'GyanDheesh Brief'."""
    prompt = f"""You are 'GyanDheesh AI', a high-end market intelligence analyst.
Your goal is 'Intelligence Compression': taking complex market signals and distilling them into a 5-minute actionable brief for students and professional traders.

Based on the structured signals below, write a high-density market brief.

RULES:
- NO trade predictions, NO buy/sell calls, NO 'institutional certainty' simulations.
- Use a calm, analytical, and professional tone.
- Highlight CONTEXT: Why does this movement matter? What is the core narrative of the day?
- Focus on: Global macro cues, domestic sector rotation, volatility regime (via PCR), and key news impact.
- Be concise but dense. Every sentence should add value.
- Use bullet points with bold headers.

STRUCTURED SIGNALS:
{json.dumps(signals, indent=2)}

Write the 'GyanDheesh Brief' now:"""

    try:
        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini summary generation error: {e}")
        return "Market summary temporarily unavailable. Please check back shortly."


async def compress_news(news_items: list[dict]) -> list[str]:
    """Compress a list of news items into concise bullet points."""
    if not news_items:
        return []

    headlines = "\n".join([f"- {item.get('title', '')}" for item in news_items[:15]])

    prompt = f"""Compress these market news headlines into 6-8 concise, factual bullet points.
Remove duplicates and noise. Keep only important, actionable information.
DO NOT add opinions or predictions. DO NOT hallucinate or add information not present in the headlines.

HEADLINES:
{headlines}

Write concise bullet points:"""

    try:
        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        lines = [l.strip().lstrip("•-* ") for l in response.text.strip().split("\n") if l.strip()]
        return [l for l in lines if len(l) > 10]
    except Exception as e:
        logger.error(f"Gemini news compression error: {e}")
        return []
