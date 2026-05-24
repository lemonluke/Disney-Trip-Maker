from src.data.disney_rides import DISNEY_RIDES
from src.data.universal_rides import UNIVERSAL_RIDES

# ── Ticket prices ─────────────────────────────────────────────────────────────
# Approximate 2025-2026 prices. Verify at official sites before booking.
# Disney pricing is date-variable; these are mid-range planning estimates.

DISNEY_TICKETS = [
    {"type": "1-Day Base (estimate — varies by date)", "price_per_person": 134.00},
    {"type": "5-Day Base (per day estimate)",          "price_per_person": 118.00},
    {"type": "5-Day Park Hopper (per day estimate)",   "price_per_person": 153.00},
    {"type": "10-Day Base (per day estimate)",         "price_per_person":  99.00},
    {"type": "10-Day Park Hopper (per day estimate)",  "price_per_person": 134.00},
]

UNIVERSAL_TICKETS = [
    {"type": "1-Day 2-Park (USF + IoA)",               "price_per_person": 124.00},
    {"type": "1-Day 3-Park (USF + IoA + Epic Universe)","price_per_person": 159.00},
    {"type": "2-Day 2-Park",                           "price_per_person": 209.00},
    {"type": "2-Day 3-Park",                           "price_per_person": 249.00},
    {"type": "3-Day 3-Park",                           "price_per_person": 259.00},
    {"type": "Express Pass (add-on, varies by date)",  "price_per_person": 130.00},
]

DISNEY_PARK_NAMES = ["Magic Kingdom", "EPCOT", "Hollywood Studios", "Animal Kingdom"]
UNIVERSAL_PARK_NAMES = ["Universal Studios Florida", "Islands of Adventure", "Epic Universe"]


def _rides_for_park(rides: list[dict], park: str) -> list[dict]:
    return [r for r in rides if r["park"] == park]


def get_disney_parks(travelers: int = 1) -> list[dict]:
    result = []
    for park in DISNEY_PARK_NAMES:
        rides = _rides_for_park(DISNEY_RIDES, park)
        tickets = [
            {**t, "total": round(t["price_per_person"] * travelers, 2)}
            for t in DISNEY_TICKETS
        ]
        result.append({"park": park, "tickets": tickets, "rides": rides})
    return result


def get_universal_parks(travelers: int = 1) -> list[dict]:
    result = []
    for park in UNIVERSAL_PARK_NAMES:
        rides = _rides_for_park(UNIVERSAL_RIDES, park)
        tickets = [
            {**t, "total": round(t["price_per_person"] * travelers, 2)}
            for t in UNIVERSAL_TICKETS
        ]
        result.append({"park": park, "tickets": tickets, "rides": rides})
    return result
