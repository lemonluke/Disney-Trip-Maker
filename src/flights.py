import time
import requests
from src.config import SERPAPI_KEY, DESTINATION_AIRPORT, MAX_FLIGHT_RESULTS

SERPAPI_URL = "https://serpapi.com/search"


def _call_serpapi(params: dict) -> dict:
    params["api_key"] = SERPAPI_KEY
    response = requests.get(SERPAPI_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _parse_flights(raw: dict, travelers: int) -> list[dict]:
    results = []
    for group in (raw.get("best_flights") or []) + (raw.get("other_flights") or []):
        legs = group.get("flights", [])
        if not legs:
            continue

        first_leg = legs[0]
        last_leg = legs[-1]
        price_per_person = group.get("price")
        if price_per_person is None:
            continue

        stops = len(legs) - 1
        stop_label = "Nonstop" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"

        airlines = list({leg.get("airline", "") for leg in legs if leg.get("airline")})
        flight_numbers = [leg.get("flight_number", "") for leg in legs if leg.get("flight_number")]

        results.append({
            "departure_time": first_leg.get("departure_airport", {}).get("time", "—"),
            "arrival_time": last_leg.get("arrival_airport", {}).get("time", "—"),
            "airline": ", ".join(airlines),
            "flight_number": " → ".join(flight_numbers),
            "stops": stop_label,
            "duration_min": group.get("total_duration", 0),
            "price_per_person": price_per_person,
            "total_price": price_per_person * travelers,
        })

        if len(results) >= MAX_FLIGHT_RESULTS:
            break

    return results


def search_flights(
    origin: str,
    outbound_date: str,
    return_date: str,
    travelers: int = 1,
) -> list[dict]:
    """Search round-trip flights from origin to MCO and back."""
    params = {
        "engine": "google_flights",
        "departure_id": origin.upper(),
        "arrival_id": DESTINATION_AIRPORT,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "adults": travelers,
        "currency": "USD",
        "hl": "en",
    }
    raw = _call_serpapi(params)
    return _parse_flights(raw, travelers)


def get_sample_price(origin: str, outbound_date: str, return_date: str) -> float | None:
    """Return cheapest round-trip price per person for a given date pair, or None if no results."""
    params = {
        "engine": "google_flights",
        "departure_id": origin.upper(),
        "arrival_id": DESTINATION_AIRPORT,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "adults": 1,
        "currency": "USD",
        "hl": "en",
    }
    try:
        raw = _call_serpapi(params)
        all_flights = (raw.get("best_flights") or []) + (raw.get("other_flights") or [])
        prices = [f["price"] for f in all_flights if f.get("price")]
        return min(prices) if prices else None
    except Exception:
        return None
    finally:
        time.sleep(0.5)
