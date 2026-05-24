from datetime import datetime
from src.config import DATE_FORMAT


def calculate_phase_nights(disney_days: int, universal_days: int) -> tuple[int, int]:
    """
    Convert park days to hotel nights using the transition-day formula:
      Disney hotel nights    = Disney days - 1
      Universal hotel nights = Universal days - 1
      Switch day is Universal night 1 (no double-counting)
    """
    phase1 = max(disney_days - 1, 0)
    phase2 = max(universal_days - 1, 0)
    return phase1, phase2


def validate_phase_vs_trip(
    phase1_nights: int,
    phase2_nights: int,
    arrival: str,
    departure: str,
) -> str | None:
    """Return a warning message if phase nights don't match the trip length, else None."""
    try:
        trip_nights = (
            datetime.strptime(departure, DATE_FORMAT) -
            datetime.strptime(arrival, DATE_FORMAT)
        ).days
    except ValueError:
        return None

    derived_total = phase1_nights + phase2_nights
    if derived_total != trip_nights:
        return (
            f"Park days imply {derived_total} hotel nights "
            f"but trip is {trip_nights} nights. "
            f"Proceeding with specific dates."
        )
    return None


def calculate_summary(
    flights: list[dict],
    disney_hotels: list[dict],
    universal_hotels: list[dict],
    disney_parks: list[dict],
    universal_parks: list[dict],
    travelers: int,
    chosen_disney_hotel_idx: int = 0,
    chosen_universal_hotel_idx: int = 0,
) -> dict:
    """
    Build cost summary using the cheapest available flight and the first hotel
    in each list (which callers can override via the idx parameters).

    Returns a dict with phase1_total, phase2_total, return_flights_total,
    grand_total, and per_person breakdowns.
    """
    # Flights — use cheapest option for outbound and assume same price for return
    flight_pp = flights[0]["price_per_person"] if flights else 0
    outbound_total = flight_pp * travelers
    return_total = outbound_total  # same route back

    # Hotels
    dh = disney_hotels[chosen_disney_hotel_idx] if disney_hotels else {}
    uh = universal_hotels[chosen_universal_hotel_idx] if universal_hotels else {}
    disney_hotel_total = dh.get("phase_total", 0)
    universal_hotel_total = uh.get("phase_total", 0)

    # Parks — use cheapest per-day ticket option as the estimate
    def cheapest_ticket_total(park_list):
        totals = []
        for park in park_list:
            for t in park.get("tickets", []):
                if t.get("total"):
                    totals.append(t["total"])
        return min(totals) if totals else 0

    disney_parks_total = cheapest_ticket_total(disney_parks)
    universal_parks_total = cheapest_ticket_total(universal_parks)

    phase1_total = outbound_total + disney_hotel_total + disney_parks_total
    phase2_total = universal_hotel_total + universal_parks_total
    grand_total = phase1_total + phase2_total + return_total

    return {
        "phase1_total": round(phase1_total, 2),
        "phase2_total": round(phase2_total, 2),
        "return_flights_total": round(return_total, 2),
        "grand_total": round(grand_total, 2),
        "per_person": round(grand_total / travelers, 2) if travelers else 0,
        "disney_hotel": dh.get("name", "—"),
        "universal_hotel": uh.get("name", "—"),
    }


def express_pass_value_note(hotel: dict, universal_days: int) -> str | None:
    """
    If the hotel includes Express Pass, calculate whether the premium over
    the cheapest Universal hotel justifies the included pass value.
    """
    if not hotel.get("express_included"):
        return None

    express_day_rate = 130  # approximate Express Pass add-on cost per person per day
    pass_value = express_day_rate * universal_days

    return (
        f"Express Pass included — approx. ${pass_value:,} value "
        f"({universal_days} days × ~${express_day_rate}/day). "
        f"Check if the hotel premium is less than this before paying separately."
    )
