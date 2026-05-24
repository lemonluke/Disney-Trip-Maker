from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from src.data.season_details import SEASON_DETAILS
from src.config import (
    GOOGLE_SHEET_ID,
    GOOGLE_CREDENTIALS_FILE,
    TAB_INPUTS,
    TAB_EXPLORE,
    TAB_MONTH_VIEW,
    TAB_FULL_PLAN,
    CELL_MODE,
    CELL_ORIGIN,
    CELL_TRAVELERS,
    CELL_MONTH_YEAR,
    CELL_ARRIVAL,
    CELL_DEPARTURE,
    CELL_DISNEY_DAYS,
    CELL_UNIVERSAL_DAYS,
    CELL_PHASE1_NIGHTS,
    CELL_PHASE2_NIGHTS,
    CELL_STATUS_MODE,
    CELL_STATUS_INPUT,
    CELL_STATUS_LAST_RUN,
    BOOKING_CELLS,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ── Connection ─────────────────────────────────────────────────────────────────

def connect() -> gspread.Spreadsheet:
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID)


# ── Reading inputs ─────────────────────────────────────────────────────────────

def read_inputs(spreadsheet: gspread.Spreadsheet) -> dict:
    ws = spreadsheet.worksheet(TAB_INPUTS)

    def cell(addr):
        val = ws.acell(addr).value
        return val.strip() if isinstance(val, str) else val

    raw_travelers = cell(CELL_TRAVELERS)
    try:
        travelers = int(raw_travelers) if raw_travelers else 1
    except ValueError:
        travelers = 1

    raw_disney_days = cell(CELL_DISNEY_DAYS)
    raw_universal_days = cell(CELL_UNIVERSAL_DAYS)
    raw_phase1 = cell(CELL_PHASE1_NIGHTS)
    raw_phase2 = cell(CELL_PHASE2_NIGHTS)

    def to_int(val):
        try:
            return int(val) if val else None
        except ValueError:
            return None

    return {
        "mode":           cell(CELL_MODE),
        "origin":         (cell(CELL_ORIGIN) or "").upper() or None,
        "travelers":      travelers,
        "month_year":     cell(CELL_MONTH_YEAR),
        "arrival":        cell(CELL_ARRIVAL),
        "departure":      cell(CELL_DEPARTURE),
        "disney_days":    to_int(raw_disney_days),
        "universal_days": to_int(raw_universal_days),
        "phase1_nights":  to_int(raw_phase1),
        "phase2_nights":  to_int(raw_phase2),
    }


# ── Status writes ──────────────────────────────────────────────────────────────

def write_status(spreadsheet: gspread.Spreadsheet, mode: str, message: str) -> None:
    ws = spreadsheet.worksheet(TAB_INPUTS)
    ws.update(CELL_STATUS_MODE, [[mode]])
    ws.update(CELL_STATUS_INPUT, [[message]])


def write_last_run(spreadsheet: gspread.Spreadsheet) -> None:
    ws = spreadsheet.worksheet(TAB_INPUTS)
    now = datetime.now()
    timestamp = f"{now.day} {now.strftime('%b %Y  %H:%M')}"
    ws.update(CELL_STATUS_LAST_RUN, [[timestamp]])


def write_phase_nights(spreadsheet: gspread.Spreadsheet, phase1: int, phase2: int) -> None:
    ws = spreadsheet.worksheet(TAB_INPUTS)
    ws.update(CELL_PHASE1_NIGHTS, [[phase1]])
    ws.update(CELL_PHASE2_NIGHTS, [[phase2]])


# ── Booking windows on Inputs tab ─────────────────────────────────────────────

def write_booking_summary(spreadsheet: gspread.Spreadsheet, booking_results: list[dict]) -> None:
    ws = spreadsheet.worksheet(TAB_INPUTS)
    for entry in booking_results:
        item = entry["item"]
        if item not in BOOKING_CELLS:
            continue
        date_cell, status_cell = BOOKING_CELLS[item]
        ws.update(date_cell, [[entry["earliest_date"]]])
        ws.update(status_cell, [[entry["status"]]])


# ── Generic helpers ────────────────────────────────────────────────────────────

def _clear_sheet(ws: gspread.Worksheet) -> None:
    ws.clear()


def _write_rows(ws: gspread.Worksheet, rows: list[list], start_row: int = 1) -> None:
    if not rows:
        return
    end_row = start_row + len(rows) - 1
    num_cols = max(len(r) for r in rows)
    end_col = chr(ord("A") + num_cols - 1)
    cell_range = f"A{start_row}:{end_col}{end_row}"
    # Pad all rows to the same width
    padded = [r + [""] * (num_cols - len(r)) for r in rows]
    ws.update(cell_range, padded)


def _header_row(labels: list[str]) -> list[str]:
    return labels


# ── Mode 1 — Explore ──────────────────────────────────────────────────────────

def write_explore_results(spreadsheet: gspread.Spreadsheet, rows: list[dict], origin: str) -> None:
    """
    rows: list of dicts with keys:
      month_label, season, avg_flight, avg_hotel_night, park_estimate, trip_total, notes,
      weather, epcot_festival, after_hours, tip
    """
    ws = spreadsheet.worksheet(TAB_EXPLORE)
    _clear_sheet(ws)

    header    = [f"24-Month Price Overview — {origin} → Orlando (MCO)", "", "", "", "", "", "", "", "", "", ""]
    subheader = ["Month", "Season", "Avg Flight (pp)", "Avg Hotel/night", "Parks (pp)",
                 "Est. Trip Total (pp)", "Notes", "Weather", "EPCOT Festival",
                 "After-Hours Events", "Planning Tip"]
    legend    = ["~ = estimated (airline seats not yet on sale for this date)", "", "", "", "", "", "", "", "", "", ""]

    output = [header, subheader, legend]
    for r in rows:
        est = r.get("is_estimated", False)
        flight_str = f"~${r['avg_flight']:.0f}" if est else f"${r['avg_flight']:.0f}" if r.get("avg_flight") else "No data"
        total_str  = f"~${r['trip_total']:.0f}"  if est else f"${r['trip_total']:.0f}"  if r.get("trip_total")  else "No data"
        output.append([
            r.get("month_label", ""),
            r.get("season", ""),
            flight_str,
            f"${r['avg_hotel_night']:.0f}" if r.get("avg_hotel_night") else "—",
            f"${r['park_estimate']:.0f}" if r.get("park_estimate") else "—",
            total_str,
            r.get("notes", ""),
            r.get("weather", ""),
            r.get("epcot_festival", ""),
            r.get("after_hours") or "—",
            r.get("tip", ""),
        ])

    _write_rows(ws, output)


# ── Mode 2 — Month View ───────────────────────────────────────────────────────

def write_month_view_results(
    spreadsheet: gspread.Spreadsheet,
    weeks: list[dict],
    month_label: str,
    travelers: int,
    booking_results: list[dict],
    month: int = 0,
) -> None:
    """
    weeks: list of dicts with keys:
      week_label, date_range, cheapest_day, priciest_day, avg_flight, avg_hotel_night, notes
    """
    ws = spreadsheet.worksheet(TAB_MONTH_VIEW)
    _clear_sheet(ws)

    output = [
        [f"Month View — {month_label}  ({travelers} traveler{'s' if travelers != 1 else ''})", "", "", "", "", ""],
        [""],
        ["Week", "Dates", "Cheapest flight day", "Priciest flight day", "Avg flight (pp)", "Avg hotel/night", "Notes"],
    ]

    for w in weeks:
        est = w.get("is_estimated", False)
        flight_str = f"~${w['avg_flight']:.0f}" if est else f"${w['avg_flight']:.0f}" if w.get("avg_flight") else "No data"
        output.append([
            w.get("week_label", ""),
            w.get("date_range", ""),
            w.get("cheapest_day", "—") if not est else "—",
            w.get("priciest_day", "—") if not est else "—",
            flight_str,
            f"${w['avg_hotel_night']:.0f}" if w.get("avg_hotel_night") else "—",
            w.get("notes", ""),
        ])

    # ── Season overview ────────────────────────────────────────────────────
    sd = SEASON_DETAILS.get(month, {}) if month else {}
    if sd:
        output += [
            [""],
            ["── SEASON OVERVIEW ──", "", "", "", "", ""],
            ["Weather",            sd.get("weather", ""),              "", "", "", ""],
            ["What to Pack",       sd.get("clothing", ""),             "", "", "", ""],
            ["EPCOT Festival",     sd.get("epcot_festival", ""),       "", "", "", ""],
            ["After-Hours Events", sd.get("after_hours") or "None this month", "", "", "", ""],
            ["Crowd Spikes",       sd.get("crowd_spikes", ""),         "", "", "", ""],
            ["Park Hours",         sd.get("park_hours", ""),           "", "", "", ""],
            ["Refurbishments",     sd.get("refurbs", ""),              "", "", "", ""],
            ["Best Weeks",         sd.get("best_weeks", ""),           "", "", "", ""],
            ["Planning Tip",       sd.get("tip", ""),                  "", "", "", ""],
        ]

    output += [[""], ["── BOOKING WINDOWS (anchored to 1st of month) ──", "", "", "", "", ""]]
    output.append(["Item", "Opens", "Earliest Date", "Status", "Notes", ""])
    for entry in booking_results:
        output.append([
            entry["item"],
            entry["rule"],
            entry["earliest_date"],
            entry["status"],
            entry["notes"],
            "",
        ])

    _write_rows(ws, output)


# ── Mode 3 — Full Plan ────────────────────────────────────────────────────────

def write_full_plan_results(
    spreadsheet: gspread.Spreadsheet,
    inputs: dict,
    flights: list[dict],
    hotels_disney: list[dict],
    hotels_universal: list[dict],
    parks_disney: list[dict],
    parks_universal: list[dict],
    booking_results: list[dict],
    summary: dict,
) -> None:
    ws = spreadsheet.worksheet(TAB_FULL_PLAN)
    _clear_sheet(ws)

    t = inputs["travelers"]
    arrival = inputs["arrival"]
    departure = inputs["departure"]
    p1 = inputs.get("phase1_nights", "?")
    p2 = inputs.get("phase2_nights", "?")

    try:
        arrival_month = int(arrival.split("/")[0])
    except (ValueError, AttributeError, IndexError):
        arrival_month = 0
    sd = SEASON_DETAILS.get(arrival_month, {})

    output = []

    # ── Trip summary ───────────────────────────────────────────────────────────
    output += [
        [f"Full Trip Plan — {arrival} to {departure}  ({t} traveler{'s' if t != 1 else ''})", "", ""],
        [""],
        ["── COST SUMMARY ──", "", ""],
        ["Category", "Total", "Per person"],
        ["Phase 1 — Disney (flights out + hotels + parks)",
            f"${summary.get('phase1_total', 0):,.2f}", f"${summary.get('phase1_total', 0) / t:,.2f}"],
        ["Phase 2 — Universal (hotels + parks)",
            f"${summary.get('phase2_total', 0):,.2f}", f"${summary.get('phase2_total', 0) / t:,.2f}"],
        ["Return flights",
            f"${summary.get('return_flights_total', 0):,.2f}", f"${summary.get('return_flights_total', 0) / t:,.2f}"],
        ["GRAND TOTAL",
            f"${summary.get('grand_total', 0):,.2f}", f"${summary.get('grand_total', 0) / t:,.2f}"],
        [""],
    ]

    # ── Trip overview — season & packing ──────────────────────────────────────
    if sd:
        output += [
            ["── TRIP OVERVIEW ──", "", ""],
            ["Weather",            sd.get("weather", ""),                        ""],
            ["What to Pack",       sd.get("clothing", ""),                       ""],
            ["EPCOT Festival",     sd.get("epcot_festival", ""),                 ""],
            ["After-Hours Events", sd.get("after_hours") or "None this month",   ""],
            ["Crowd Spikes",       sd.get("crowd_spikes", ""),                   ""],
            ["Park Hours",         sd.get("park_hours", ""),                     ""],
            ["Refurbishments",     sd.get("refurbs", ""),                        ""],
            ["Best Weeks",         sd.get("best_weeks", ""),                     ""],
            ["Planning Tip",       sd.get("tip", ""),                            ""],
            [""],
        ]

    # ── Flights ────────────────────────────────────────────────────────────────
    output += [
        ["── FLIGHTS ──", "", "", "", "", ""],
        ["#", "Departs", "Arrives", "Airline / Flight", "Stops", "Price (pp)", "Total"],
    ]
    for i, f in enumerate(flights, 1):
        output.append([
            i,
            f.get("departure_time", "—"),
            f.get("arrival_time", "—"),
            f"{f.get('airline', '')}  {f.get('flight_number', '')}".strip(),
            f.get("stops", "—"),
            f"${f.get('price_per_person', 0):,.2f}",
            f"${f.get('total_price', 0):,.2f}",
        ])
    output.append([""])

    # ── Hotels — Disney (Phase 1) ──────────────────────────────────────────────
    output += [
        [f"── HOTELS — DISNEY  (Phase 1 · {p1} nights) ──", "", "", "", "", "", "", "", "", ""],
        ["Hotel", "Location", "Stars", "Price/night", f"Phase 1 total ({p1} nights)",
         "Dist. MK", "Dist. EPCOT", "Dist. HS", "Dist. AK", "On-site perks"],
    ]
    for h in hotels_disney:
        output.append([
            h.get("name", ""),
            h.get("location_tag", ""),
            h.get("stars", ""),
            f"${h.get('price_per_night', 0):,.2f}",
            f"${h.get('phase_total', 0):,.2f}",
            h.get("dist_mk", "—"),
            h.get("dist_epcot", "—"),
            h.get("dist_hs", "—"),
            h.get("dist_ak", "—"),
            h.get("perks", ""),
        ])
    output.append([""])

    # ── Hotels — Universal (Phase 2) ──────────────────────────────────────────
    output += [
        [f"── HOTELS — UNIVERSAL  (Phase 2 · {p2} nights) ──", "", "", "", "", "", "", "", ""],
        ["Hotel", "Location", "Stars", "Price/night", f"Phase 2 total ({p2} nights)",
         "Dist. USF", "Dist. IoA", "Dist. Epic Universe", "On-site perks"],
    ]
    for h in hotels_universal:
        output.append([
            h.get("name", ""),
            h.get("location_tag", ""),
            h.get("stars", ""),
            f"${h.get('price_per_night', 0):,.2f}",
            f"${h.get('phase_total', 0):,.2f}",
            h.get("dist_usf", "—"),
            h.get("dist_ioa", "—"),
            h.get("dist_epic", "—"),
            h.get("perks", ""),
        ])
    output.append([""])

    # ── Parks — Disney ─────────────────────────────────────────────────────────
    output.append(["── PARKS — DISNEY ──", "", "", "", ""])
    for park_data in parks_disney:
        output.append([park_data["park"], "", "", "", ""])
        output.append(["Ticket type", "Price (pp)", f"Total ({t} travelers)", "", ""])
        for ticket in park_data.get("tickets", []):
            output.append([
                ticket.get("type", ""),
                f"${ticket.get('price_per_person', 0):,.2f}",
                f"${ticket.get('price_per_person', 0) * t:,.2f}",
                "",
                "",
            ])
        output.append(["Ride", "Thrill level", "Height req", "Lightning Lane", "Notes"])
        for ride in park_data.get("rides", []):
            output.append([
                ride.get("name", ""),
                ride.get("thrill_level", ""),
                ride.get("height_req") or "None",
                ride.get("lightning_lane", "None"),
                ride.get("notes", ""),
            ])
        output.append([""])

    # ── Parks — Universal ──────────────────────────────────────────────────────
    output.append(["── PARKS — UNIVERSAL ──", "", "", "", ""])
    for park_data in parks_universal:
        output.append([park_data["park"], "", "", "", ""])
        output.append(["Ticket type", "Price (pp)", f"Total ({t} travelers)", "", ""])
        for ticket in park_data.get("tickets", []):
            output.append([
                ticket.get("type", ""),
                f"${ticket.get('price_per_person', 0):,.2f}",
                f"${ticket.get('price_per_person', 0) * t:,.2f}",
                "",
                "",
            ])
        output.append(["Ride", "Thrill level", "Height req", "Express Pass", "Notes"])
        for ride in park_data.get("rides", []):
            output.append([
                ride.get("name", ""),
                ride.get("thrill_level", ""),
                ride.get("height_req") or "None",
                ride.get("express_pass", "None"),
                ride.get("notes", ""),
            ])
        output.append([""])

    # ── Booking windows ────────────────────────────────────────────────────────
    output += [
        ["── BOOKING WINDOWS ──", "", "", "", "", "", "", ""],
        ["Category", "Item", "Rule", "Earliest date", "Status", "Notes", "Booking URL", ""],
    ]
    for entry in booking_results:
        output.append([
            _booking_category(entry["item"]),
            entry["item"],
            entry["rule"],
            entry["earliest_date"],
            entry["status"],
            entry["notes"],
            entry.get("url", "—"),
            "",
        ])

    _write_rows(ws, output)


def _booking_category(item: str) -> str:
    if "flight" in item.lower():
        return "Flights"
    if "hotel" in item.lower():
        return "Hotels"
    if "dining" in item.lower():
        return "Dining"
    if "lightning" in item.lower() or "pass" in item.lower():
        return "Fast Pass"
    return "Parks"
