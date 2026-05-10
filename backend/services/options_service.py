"""Options data processing from NSE option chain endpoints."""

import logging
from normalizer.normalize import normalize_strike_oi, ts_now
from services.nse_service import nse

logger = logging.getLogger(__name__)


def _calculate_max_pain(data: list[dict]) -> float:
    """Calculate max pain strike — the strike where option writers lose the least."""
    strikes = set()
    call_oi_map = {}
    put_oi_map = {}

    for item in data:
        strike = item.get("strikePrice", 0)
        strikes.add(strike)
        if "CE" in item:
            call_oi_map[strike] = item["CE"].get("openInterest", 0)
        if "PE" in item:
            put_oi_map[strike] = item["PE"].get("openInterest", 0)

    if not strikes:
        return 0

    min_loss = float("inf")
    max_pain_strike = 0

    for test_strike in sorted(strikes):
        total_loss = 0
        for s in strikes:
            # Call writers lose if expiry > strike
            if test_strike > s:
                total_loss += (test_strike - s) * call_oi_map.get(s, 0)
            # Put writers lose if expiry < strike
            if test_strike < s:
                total_loss += (s - test_strike) * put_oi_map.get(s, 0)
        if total_loss < min_loss:
            min_loss = total_loss
            max_pain_strike = test_strike

    return max_pain_strike


async def fetch_options_snapshot(symbol: str = "NIFTY") -> dict | None:
    """Fetch and process option chain data for a given index."""
    raw = await nse.get_option_chain(symbol)
    if not raw:
        return None

    try:
        records = raw.get("records", {})
        all_data = records.get("data", [])
        underlying = records.get("underlyingValue", 0)

        total_call_oi = 0
        total_put_oi = 0
        call_strikes = {}
        put_strikes = {}

        for item in all_data:
            strike = item.get("strikePrice", 0)

            if "CE" in item:
                oi = item["CE"].get("openInterest", 0)
                chg = item["CE"].get("changeinOpenInterest", 0)
                total_call_oi += oi
                call_strikes[strike] = {"oi": oi, "change_oi": chg}

            if "PE" in item:
                oi = item["PE"].get("openInterest", 0)
                chg = item["PE"].get("changeinOpenInterest", 0)
                total_put_oi += oi
                put_strikes[strike] = {"oi": oi, "change_oi": chg}

        pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0

        max_pain = _calculate_max_pain(all_data)

        # Top 5 strikes by OI
        top_calls = sorted(call_strikes.items(), key=lambda x: x[1]["oi"], reverse=True)[:5]
        top_puts = sorted(put_strikes.items(), key=lambda x: x[1]["oi"], reverse=True)[:5]

        top_call_oi = [
            normalize_strike_oi(s, d["oi"], d["change_oi"]).model_dump()
            for s, d in top_calls
        ]
        top_put_oi = [
            normalize_strike_oi(s, d["oi"], d["change_oi"]).model_dump()
            for s, d in top_puts
        ]

        # Support = high put OI zones, Resistance = high call OI zones
        resistance = sorted([s for s, _ in top_calls[:3]])
        support = sorted([s for s, _ in top_puts[:3]])

        return {
            "symbol": symbol,
            "pcr": pcr,
            "max_pain": max_pain,
            "top_call_oi": top_call_oi,
            "top_put_oi": top_put_oi,
            "support_levels": support,
            "resistance_levels": resistance,
            "updated_at": ts_now(),
        }

    except Exception as e:
        logger.error(f"Options processing error: {e}")
        return None
