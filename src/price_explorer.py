from datetime import date, timedelta
import calendar
import time
from src.flights import get_sample_price
from src.config import SEASONS, HIGH_DEMAND_NOTES

# Baseline hotel nightly rates by month (mid-range on-site Disney estimate)
HOTEL_RATES = {
    1: 155, 2: 165, 3: 225, 4: 215, 5: 205,
    6: 295, 7: 330, 8: 245, 9: 170, 10: 200,
    11: 220, 12: 370,
}

# Rough per-person park estimate for a 7-night reference trip
# (4 Disney days + 2 Universal days at ~$130 and ~$125 respectively)
PARK_ESTIMATE_PP = 770


def _season_tag(month: int) -> str:
    for label, months in SEASONS.items():
        if month in months:
            return label
    return "Moderate"


def _sample_dates_for_month(year: int, month: int) -> list[tuple[str, str]]:
    """Return 2 (outbound, return) date pairs sampling the month: early and mid."""
    pairs = []
    for start_day in (7, 18):
        try:
            outbound = date(year, month, start_day)
        except ValueError:
            continue
        if outbound <= date.today():
            continue
        return_date = outbound + timedelta(days=7)
        if return_date.month != month:
            return_date = date(year, month, calendar.monthrange(year, month)[1])
        pairs.append((outbound.strftime("%Y-%m-%d"), return_date.strftime("%Y-%m-%d")))
    return pairs


def build_explore_grid(origin: str, travelers: int = 1) -> list[dict]:
    """Mode 1 — generate a 24-month price overview."""
    today = date.today()
    start = date(today.year, today.month, 1) + timedelta(days=32)
    start = date(start.year, start.month, 1)

    rows = []
    for i in range(24):
        m = start.month + i
        year = start.year + (m - 1) // 12
        month = ((m - 1) % 12) + 1
        month_label = date(year, month, 1).strftime("%b %Y")

        sample_pairs = _sample_dates_for_month(year, month)
        prices = []
        for outbound, ret in sample_pairs:
            p = get_sample_price(origin, outbound, ret)
            if p:
                prices.append(p)
            time.sleep(0.5)

        avg_flight = sum(prices) / len(prices) if prices else None
        hotel_nightly = HOTEL_RATES.get(month, 200)
        trip_total = (avg_flight + hotel_nightly * 7 + PARK_ESTIMATE_PP) if avg_flight else None

        rows.append({
            "month_label": month_label,
            "season": _season_tag(month),
            "avg_flight": avg_flight,
            "avg_hotel_night": hotel_nightly,
            "park_estimate": PARK_ESTIMATE_PP,
            "trip_total": trip_total,
            "notes": HIGH_DEMAND_NOTES.get(month, ""),
        })

    return rows


def build_month_view(origin: str, month_year: str, travelers: int = 1) -> list[dict]:
    """Mode 2 — week-by-week breakdown for a given month (MM/YYYY)."""
    month, year = int(month_year[:2]), int(month_year[3:])
    days_in_month = calendar.monthrange(year, month)[1]
    hotel_nightly = HOTEL_RATES.get(month, 200)

    # Split month into roughly 4 weekly windows
    week_ranges = []
    starts = [1, 8, 15, 22]
    for idx, s in enumerate(starts):
        e = starts[idx + 1] - 1 if idx + 1 < len(starts) else days_in_month
        week_ranges.append((s, e))

    weeks = []
    for idx, (day_start, day_end) in enumerate(week_ranges, 1):
        week_label = f"Week {idx}"
        date_range = (
            f"{date(year, month, day_start).strftime('%b %-d')} – "
            f"{date(year, month, day_end).strftime('%-d')}"
        )

        # Sample Tuesday and Thursday of the week
        sample_prices = []
        cheapest_day = None
        priciest_day = None
        for offset in (1, 3):
            d = day_start + offset
            if d > days_in_month:
                continue
            outbound = date(year, month, d)
            if outbound <= date.today():
                continue
            ret = outbound + timedelta(days=7)
            p = get_sample_price(origin, outbound.strftime("%Y-%m-%d"), ret.strftime("%Y-%m-%d"))
            if p:
                sample_prices.append((outbound.strftime("%b %-d"), p))
            time.sleep(0.5)

        avg_flight = None
        if sample_prices:
            avg_flight = sum(p for _, p in sample_prices) / len(sample_prices)
            cheapest_day = min(sample_prices, key=lambda x: x[1])[0]
            priciest_day = max(sample_prices, key=lambda x: x[1])[0]

        # Basic event notes
        notes = HIGH_DEMAND_NOTES.get(month, "")
        if month == 12 and day_start >= 22:
            notes = "Christmas week — peak crowds and prices"
        elif month == 3 and 8 <= day_start <= 22:
            notes = "Spring Break peak window"
        elif month == 11 and day_start >= 22:
            notes = "Thanksgiving week"

        weeks.append({
            "week_label": week_label,
            "date_range": date_range,
            "cheapest_day": cheapest_day or "—",
            "priciest_day": priciest_day or "—",
            "avg_flight": avg_flight,
            "avg_hotel_night": hotel_nightly,
            "notes": notes,
        })

    return weeks
