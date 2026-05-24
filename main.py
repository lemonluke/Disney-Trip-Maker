"""
Disney Florida Trip Planner
Run: python main.py
"""

import time
from datetime import datetime
from src import sheets, flights, price_explorer, hotels, parks, trip_strategy, report
from src.booking_windows import calculate_booking_windows
from src.config import MODE_EXPLORE, MODE_MONTH_VIEW, MODE_FULL_PLAN, DATE_FORMAT, DATE_FORMAT_API, MONTH_FORMAT


def _fmt_elapsed(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}h {m:02d}m {s:02d}s"


def _parse_date(val: str | None):
    if not val:
        return None
    try:
        return datetime.strptime(val.strip(), DATE_FORMAT).date()
    except ValueError:
        return None


def _parse_month(val: str | None) -> str | None:
    if not val:
        return None
    try:
        datetime.strptime(val.strip(), MONTH_FORMAT)
        return val.strip()
    except ValueError:
        return None


def _run():
    report.console.rule("[bold blue]Disney Trip Planner[/bold blue]")

    # ── Connect ────────────────────────────────────────────────────────────────
    report.print_status("Connecting to Google Sheets...")
    try:
        spreadsheet = sheets.connect()
    except Exception as e:
        report.print_error(f"Could not connect to Google Sheets: {e}")
        return
    report.print_status("Connected.")

    # ── Read inputs ────────────────────────────────────────────────────────────
    inputs = sheets.read_inputs(spreadsheet)
    mode      = (inputs.get("mode") or "").strip()
    origin    = inputs.get("origin")
    travelers = inputs.get("travelers") or 1

    # ── Validate origin ────────────────────────────────────────────────────────
    if not origin:
        sheets.write_status(spreadsheet, mode or "—",
                            "Origin airport is required. Please fill in cell B4.")
        report.print_error("Origin airport (B4) is required. Fill it in and re-run.")
        return

    report.print_status(f"Origin: {origin}  |  Travelers: {travelers}  |  Mode: {mode}")

    # ── MODE 1 — Explore ───────────────────────────────────────────────────────
    if mode == MODE_EXPLORE:
        sheets.write_status(spreadsheet, MODE_EXPLORE,
                            "Running — generating 24-month price overview...")
        report.print_status("Mode: Explore — building 24-month price grid...")

        rows = price_explorer.build_explore_grid(origin, travelers)
        sheets.write_explore_results(spreadsheet, rows, origin)
        sheets.write_last_run(spreadsheet)
        sheets.write_status(spreadsheet, MODE_EXPLORE, "Done — see 1 - Explore sheet.")

        report.print_explore_report(origin, rows)
        report.print_done("1 - Explore")
        return

    # ── MODE 2 — Month View ────────────────────────────────────────────────────
    if mode == MODE_MONTH_VIEW:
        month_year = _parse_month(inputs.get("month_year"))
        if not month_year:
            msg = f"Month + Year is required for Month View. Please fill in cell B8 (format: MM/YYYY)."
            sheets.write_status(spreadsheet, MODE_MONTH_VIEW, msg)
            report.print_error(msg)
            return

        sheets.write_status(spreadsheet, MODE_MONTH_VIEW,
                            f"Running — showing prices for {month_year}...")
        report.print_status(f"Mode: Month View — {month_year}")

        from datetime import date as date_cls
        month, year = int(month_year[:2]), int(month_year[3:])
        anchor = date_cls(year, month, 1)
        booking_results = calculate_booking_windows(anchor, anchor)

        weeks = price_explorer.build_month_view(origin, month_year, travelers)
        month_label = datetime.strptime(month_year, MONTH_FORMAT).strftime("%B %Y")

        sheets.write_month_view_results(spreadsheet, weeks, month_label, travelers, booking_results)
        sheets.write_last_run(spreadsheet)
        sheets.write_status(spreadsheet, MODE_MONTH_VIEW, "Done — see 2 - Month View sheet.")

        report.print_month_view_report(month_label, weeks, travelers)
        report.print_done("2 - Month View")
        return

    # ── MODE 3 — Full Plan ─────────────────────────────────────────────────────
    if mode == MODE_FULL_PLAN:
        arrival   = _parse_date(inputs.get("arrival"))
        departure = _parse_date(inputs.get("departure"))

        if not arrival:
            msg = "Arrival date is required for Full Plan. Please fill in cell B11 (format: MM/DD/YYYY)."
            sheets.write_status(spreadsheet, MODE_FULL_PLAN, msg)
            report.print_error(msg)
            return
        if not departure:
            msg = "Departure date is required. Please fill in cell B12 (format: MM/DD/YYYY)."
            sheets.write_status(spreadsheet, MODE_FULL_PLAN, msg)
            report.print_error(msg)
            return
        if departure <= arrival:
            msg = "Departure date must be after arrival date."
            sheets.write_status(spreadsheet, MODE_FULL_PLAN, msg)
            report.print_error(msg)
            return

        # Cross-check month/year if filled in
        month_year = inputs.get("month_year")
        if month_year and _parse_month(month_year):
            arrival_my = arrival.strftime(MONTH_FORMAT)
            if month_year.strip() != arrival_my:
                msg = (f"Month/Year ({month_year}) conflicts with arrival date "
                       f"({inputs['arrival']}). Please correct or clear cell B8.")
                sheets.write_status(spreadsheet, "Conflict", msg)
                report.print_error(msg)
                return

        sheets.write_status(spreadsheet, MODE_FULL_PLAN,
                            f"Running — full plan for {inputs['arrival']} to {inputs['departure']}...")

        # API-format dates for Serpapi and internal modules (always YYYY-MM-DD)
        arrival_api   = arrival.strftime(DATE_FORMAT_API)
        departure_api = departure.strftime(DATE_FORMAT_API)

        # ── Phase night calculation ────────────────────────────────────────────
        disney_days    = inputs.get("disney_days")
        universal_days = inputs.get("universal_days")
        phase1 = inputs.get("phase1_nights")
        phase2 = inputs.get("phase2_nights")

        if disney_days and universal_days:
            phase1, phase2 = trip_strategy.calculate_phase_nights(disney_days, universal_days)
            sheets.write_phase_nights(spreadsheet, phase1, phase2)
            report.print_status(f"Phase nights: Disney={phase1}, Universal={phase2}")
        elif not phase1 or not phase2:
            trip_nights = (departure - arrival).days
            phase1 = round(trip_nights * 0.7)
            phase2 = trip_nights - phase1
            report.print_warning(
                f"No park days provided — defaulting to {phase1} Disney / {phase2} Universal nights."
            )

        warn = trip_strategy.validate_phase_vs_trip(phase1, phase2, arrival_api, departure_api)
        if warn:
            report.print_warning(warn)

        inputs["arrival"]       = inputs["arrival"]
        inputs["departure"]     = inputs["departure"]
        inputs["phase1_nights"] = phase1
        inputs["phase2_nights"] = phase2

        # ── Booking windows ────────────────────────────────────────────────────
        report.print_status("Calculating booking windows...")
        booking_results = calculate_booking_windows(arrival, departure)
        sheets.write_booking_summary(spreadsheet, booking_results)

        # ── Flights ────────────────────────────────────────────────────────────
        report.print_status(f"Searching flights {origin} → MCO...")
        try:
            flight_results = flights.search_flights(origin, arrival_api, departure_api, travelers)
        except Exception as e:
            report.print_warning(f"Flight search failed: {e}. Continuing without flight data.")
            flight_results = []

        # ── Hotels ────────────────────────────────────────────────────────────
        report.print_status("Loading hotel options...")
        disney_hotels_list    = hotels.get_disney_hotels(phase1, arrival_api)
        universal_hotels_list = hotels.get_universal_hotels(phase2, arrival_api)

        # ── Parks ─────────────────────────────────────────────────────────────
        report.print_status("Loading park data...")
        disney_park_data    = parks.get_disney_parks(travelers)
        universal_park_data = parks.get_universal_parks(travelers)

        # ── Summary ───────────────────────────────────────────────────────────
        summary = trip_strategy.calculate_summary(
            flight_results, disney_hotels_list, universal_hotels_list,
            disney_park_data, universal_park_data, travelers,
        )

        ep_note = trip_strategy.express_pass_value_note(
            universal_hotels_list[0] if universal_hotels_list else {},
            universal_days or phase2,
        )
        if ep_note:
            report.print_warning(ep_note)

        # ── Write to sheet ─────────────────────────────────────────────────────
        report.print_status("Writing results to 3 - Full Plan...")
        sheets.write_full_plan_results(
            spreadsheet, inputs,
            flight_results, disney_hotels_list, universal_hotels_list,
            disney_park_data, universal_park_data,
            booking_results, summary,
        )
        sheets.write_last_run(spreadsheet)
        sheets.write_status(spreadsheet, MODE_FULL_PLAN,
                            f"Done — {inputs['arrival']} to {inputs['departure']}. See 3 - Full Plan.")

        report.print_full_plan_report(inputs, summary, flight_results)
        report.print_done("3 - Full Plan")
        return

    # ── Unknown mode ───────────────────────────────────────────────────────────
    msg = f"Unknown mode '{mode}'. Select Explore, Month View, or Full Plan from the dropdown in B3."
    sheets.write_status(spreadsheet, mode or "—", msg)
    report.print_error(msg)


def main():
    start = time.perf_counter()
    try:
        _run()
    finally:
        elapsed = time.perf_counter() - start
        report.console.print(f"\n[dim]Completed in {_fmt_elapsed(elapsed)}[/dim]")


if __name__ == "__main__":
    main()
