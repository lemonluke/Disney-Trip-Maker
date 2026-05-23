from datetime import date, timedelta

BOOKING_WINDOWS = {
    "American Airlines flights": {
        "days_before": 331,
        "anchor": "departure_date",
        "notes": "AA opens exactly 331 days before departure. Set a calendar reminder.",
        "url": "https://www.aa.com",
    },
    "Disney Resort hotels": {
        "days_before": 499,
        "anchor": "arrival_date",
        "notes": "General public window. Disney Vacation Club members may access earlier. EPCOT-area resorts sell out fast for peak dates.",
        "url": "https://disneyworld.disney.go.com/reservations/hotels/",
    },
    "Universal on-site hotels": {
        "days_before": 365,
        "anchor": "arrival_date",
        "notes": "No strict cutoff but inventory is limited — Premier hotels with Express Pass included book fast.",
        "url": "https://www.universalorlando.com/web/en/us/hotels",
    },
    "Off-site hotels": {
        "days_before": 365,
        "anchor": "arrival_date",
        "notes": "Varies by property. Flexible cancellation off-site gives more room to rebook.",
        "url": None,
    },
    "Disney park tickets": {
        "days_before": None,
        "anchor": None,
        "notes": "No advance window — available any time. Prices increase closer to date so buy early to lock in lower price.",
        "url": "https://disneyworld.disney.go.com/admission/tickets/",
    },
    "Lightning Lane Multi Pass": {
        "days_before": 0,
        "anchor": "park_date",
        "notes": "Day-of purchase only at 7:00am. On-site Disney Resort guests can purchase from their resort.",
        "url": "https://disneyworld.disney.go.com/experience-updates/lightning-lane/",
    },
    "Lightning Lane Single Pass": {
        "days_before": 0,
        "anchor": "park_date",
        "notes": "Day-of only at 7:00am. Most in-demand rides (TRON, Seven Dwarfs, Rise of the Resistance, Avatar FoP) sell out within minutes.",
        "url": "https://disneyworld.disney.go.com/experience-updates/lightning-lane/",
    },
    "Universal park tickets": {
        "days_before": None,
        "anchor": None,
        "notes": "No hard advance booking window. Prices do not vary by purchase date the way Disney's do.",
        "url": "https://www.universalorlando.com/web/en/us/tickets-passes/base-tickets",
    },
    "Universal Express Pass": {
        "days_before": None,
        "anchor": None,
        "notes": "Purchase any time in advance. Included free with Premier on-site hotels — check if the hotel rate offset is worthwhile before buying separately.",
        "url": "https://www.universalorlando.com/web/en/us/tickets-passes/express-pass",
    },
    "Disney dining reservations": {
        "days_before": 60,
        "anchor": "dining_date",
        "notes": "Most popular restaurants (Be Our Guest, Space 220, Ohana, Topolino's) book within hours of opening. Set an alarm for 6:00am on your 60-day window.",
        "url": "https://disneyworld.disney.go.com/dining/",
    },
}


def _status_label(earliest: date | None, days_before: int | None) -> str:
    if days_before is None:
        return "Available any time"
    if days_before == 0:
        return "Day-of purchase only"
    if earliest is None:
        return "Date needed to calculate"

    today = date.today()
    delta = (earliest - today).days

    if delta > 0:
        return f"Opens in {delta} days ({earliest.strftime('%d %b %Y')})"
    elif delta == 0:
        return "OPENS TODAY"
    else:
        return "OPEN — book now"


def calculate_booking_windows(arrival_date: date, departure_date: date) -> list[dict]:
    results = []

    for item_name, rule in BOOKING_WINDOWS.items():
        days_before = rule["days_before"]
        anchor_key = rule["anchor"]

        if days_before is None or anchor_key is None:
            earliest = None
        elif anchor_key == "departure_date":
            earliest = departure_date - timedelta(days=days_before)
        else:
            # arrival_date, park_date, dining_date all use arrival as the anchor
            # (park_date and dining_date are per-day lookups — arrival is the conservative estimate)
            earliest = arrival_date - timedelta(days=days_before)

        results.append({
            "item": item_name,
            "rule": (
                f"Available any time" if days_before is None
                else f"Day-of only" if days_before == 0
                else f"Opens {days_before} days before {anchor_key.replace('_', ' ')}"
            ),
            "earliest_date": earliest.strftime("%Y-%m-%d") if earliest else "—",
            "status": _status_label(earliest, days_before),
            "notes": rule["notes"],
            "url": rule["url"] or "—",
        })

    return results
