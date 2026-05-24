from datetime import date, timedelta
import calendar
import time
from src.flights import get_sample_price
from src.config import SEASONS, HIGH_DEMAND_NOTES
from src.data.season_details import SEASON_DETAILS

# Baseline hotel nightly rates by month (mid-range on-site Disney estimate)
HOTEL_RATES = {
    1: 155, 2: 165, 3: 225, 4: 215, 5: 205,
    6: 295, 7: 330, 8: 245, 9: 170, 10: 200,
    11: 220, 12: 370,
}

# Fallback flight prices per season when no live data is available
# (round-trip economy estimate — used only when booking window is not yet open)
FLIGHT_FALLBACK = {
    "Value":    295,
    "Moderate": 375,
    "Peak":     540,
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


def _fill_estimated_prices(rows: list[dict]) -> list[dict]:
    """
    For any row where avg_flight is None (booking window not yet open),
    estimate from the average of real prices for the same season collected
    in this run. Falls back to FLIGHT_FALLBACK if no same-season data exists.
    Marks estimated rows with is_estimated=True.
    """
    # Collect real prices by season
    real_by_season: dict[str, list[float]] = {"Value": [], "Moderate": [], "Peak": []}
    for row in rows:
        if row.get("avg_flight") and not row.get("is_estimated"):
            real_by_season[row["season"]].append(row["avg_flight"])

    # Build per-season estimate (real average, else hardcoded fallback)
    season_estimate = {
        s: sum(prices) / len(prices) if prices else FLIGHT_FALLBACK[s]
        for s, prices in real_by_season.items()
    }

    for row in rows:
        if row["avg_flight"] is None:
            estimate = round(season_estimate[row["season"]])
            row["avg_flight"] = estimate
            row["is_estimated"] = True
            row["trip_total"] = estimate + row["avg_hotel_night"] * 7 + PARK_ESTIMATE_PP

    return rows


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
        season = _season_tag(month)

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

        sd = SEASON_DETAILS.get(month, {})
        rows.append({
            "month_label": month_label,
            "season": season,
            "avg_flight": avg_flight,
            "is_estimated": False,
            "avg_hotel_night": hotel_nightly,
            "park_estimate": PARK_ESTIMATE_PP,
            "trip_total": trip_total,
            "notes": HIGH_DEMAND_NOTES.get(month, ""),
            "weather":        sd.get("weather", ""),
            "epcot_festival": sd.get("epcot_festival", ""),
            "after_hours":    sd.get("after_hours") or "",
            "best_weeks":     sd.get("best_weeks", ""),
            "tip":            sd.get("tip", ""),
        })

    return _fill_estimated_prices(rows)


def build_month_view(origin: str, month_year: str, travelers: int = 1) -> list[dict]:
    """Mode 2 — week-by-week breakdown for a given month (MM/YYYY)."""
    month, year = (int(p) for p in month_year.split("/"))
    days_in_month = calendar.monthrange(year, month)[1]
    hotel_nightly = HOTEL_RATES.get(month, 200)
    season = _season_tag(month)

    week_ranges = []
    starts = [1, 8, 15, 22]
    for idx, s in enumerate(starts):
        e = starts[idx + 1] - 1 if idx + 1 < len(starts) else days_in_month
        week_ranges.append((s, e))

    weeks = []
    real_prices = []

    for idx, (day_start, day_end) in enumerate(week_ranges, 1):
        week_label = f"Week {idx}"
        date_range = f"{date(year, month, day_start).strftime('%b')} {day_start} – {day_end}"

        sample_prices = []
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
                sample_prices.append((f"{outbound.strftime('%b')} {outbound.day}", p))
            time.sleep(0.5)

        avg_flight = None
        cheapest_day = None
        priciest_day = None
        is_estimated = False

        if sample_prices:
            real_prices.extend(p for _, p in sample_prices)
            avg_flight = sum(p for _, p in sample_prices) / len(sample_prices)
            cheapest_day = min(sample_prices, key=lambda x: x[1])[0]
            priciest_day = max(sample_prices, key=lambda x: x[1])[0]

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
            "is_estimated": is_estimated,
            "avg_hotel_night": hotel_nightly,
            "notes": notes,
        })

    # Fill weeks with no live data using the average of weeks that had data,
    # falling back to the seasonal default
    if real_prices:
        week_estimate = round(sum(real_prices) / len(real_prices))
    else:
        week_estimate = FLIGHT_FALLBACK[season]

    for week in weeks:
        if week["avg_flight"] is None:
            week["avg_flight"] = week_estimate
            week["is_estimated"] = True

    return weeks
