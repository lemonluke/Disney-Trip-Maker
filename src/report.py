from rich.console import Console
from rich.table import Table
from rich.rule import Rule
from rich import box

console = Console()


def print_explore_report(origin: str, rows: list[dict]) -> None:
    console.print()
    console.rule(f"[bold blue]PRICE OVERVIEW — {origin} → Orlando (MCO)[/bold blue]")

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    table.add_column("Month",        style="cyan",  min_width=10)
    table.add_column("Season",       style="yellow", min_width=10)
    table.add_column("Avg Flight",   justify="right", min_width=12)
    table.add_column("Hotel/night",  justify="right", min_width=12)
    table.add_column("Trip Est. (pp)",justify="right", min_width=14)
    table.add_column("Notes",        style="dim",   min_width=30)

    for r in rows:
        flight = f"${r['avg_flight']:,.0f}" if r.get("avg_flight") else "[dim]No data[/dim]"
        hotel  = f"${r['avg_hotel_night']:,.0f}" if r.get("avg_hotel_night") else "—"
        total  = f"${r['trip_total']:,.0f}" if r.get("trip_total") else "[dim]No data[/dim]"
        season_colour = {"Value": "green", "Moderate": "yellow", "Peak": "red"}.get(r["season"], "white")
        table.add_row(
            r["month_label"],
            f"[{season_colour}]{r['season']}[/{season_colour}]",
            flight, hotel, total,
            r.get("notes", ""),
        )

    console.print(table)
    console.print("[dim]Prices are estimates based on sample dates. Use Mode 3 for accurate quotes.[/dim]")
    console.print()


def print_month_view_report(month_label: str, weeks: list[dict], travelers: int) -> None:
    console.print()
    console.rule(f"[bold blue]{month_label} — Week-by-Week ({travelers} traveler{'s' if travelers != 1 else ''})[/bold blue]")

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    table.add_column("Week",          style="cyan",  min_width=8)
    table.add_column("Dates",         min_width=14)
    table.add_column("Cheapest day",  min_width=10)
    table.add_column("Priciest day",  min_width=10)
    table.add_column("Avg Flight",    justify="right", min_width=12)
    table.add_column("Hotel/night",   justify="right", min_width=12)
    table.add_column("Notes",         style="dim",   min_width=28)

    for w in weeks:
        flight = f"${w['avg_flight']:,.0f}" if w.get("avg_flight") else "[dim]No data[/dim]"
        hotel  = f"${w['avg_hotel_night']:,.0f}" if w.get("avg_hotel_night") else "—"
        table.add_row(
            w["week_label"], w["date_range"],
            w["cheapest_day"], w["priciest_day"],
            flight, hotel, w.get("notes", ""),
        )

    console.print(table)
    console.print()


def print_full_plan_report(inputs: dict, summary: dict, flights: list[dict]) -> None:
    t = inputs["travelers"]
    console.print()
    console.rule(f"[bold blue]FULL TRIP PLAN — {inputs['arrival']} to {inputs['departure']} · {t} traveler{'s' if t != 1 else ''}[/bold blue]")

    # Cost summary
    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold", title="Cost Summary")
    table.add_column("Category",    min_width=45)
    table.add_column("Total",       justify="right", min_width=14)
    table.add_column("Per person",  justify="right", min_width=14)

    def row(label, total):
        return label, f"${total:,.2f}", f"${total / t:,.2f}"

    table.add_row(*row(f"Phase 1 — Disney  ({summary['disney_hotel']})", summary["phase1_total"]))
    table.add_row(*row(f"Phase 2 — Universal  ({summary['universal_hotel']})", summary["phase2_total"]))
    table.add_row(*row("Return flights", summary["return_flights_total"]))
    table.add_section()
    table.add_row(
        "[bold]GRAND TOTAL[/bold]",
        f"[bold]${summary['grand_total']:,.2f}[/bold]",
        f"[bold]${summary['per_person']:,.2f}[/bold]",
    )
    console.print(table)

    # Top flight options
    if flights:
        console.print()
        console.rule("[bold]Top Flight Options[/bold]", style="dim")
        ftable = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        ftable.add_column("#",         width=3)
        ftable.add_column("Departs",   min_width=18)
        ftable.add_column("Arrives",   min_width=18)
        ftable.add_column("Airline",   min_width=20)
        ftable.add_column("Stops",     min_width=10)
        ftable.add_column("Price (pp)",justify="right", min_width=12)
        ftable.add_column("Total",     justify="right", min_width=12)

        for i, f in enumerate(flights, 1):
            ftable.add_row(
                str(i),
                f.get("departure_time", "—"),
                f.get("arrival_time", "—"),
                f"{f.get('airline', '')} {f.get('flight_number', '')}".strip(),
                f.get("stops", "—"),
                f"${f.get('price_per_person', 0):,.2f}",
                f"${f.get('total_price', 0):,.2f}",
            )
        console.print(ftable)

    console.print()
    console.print("[green]✓ Google Sheet updated — see 3 - Full Plan tab.[/green]")
    console.print()


def print_status(message: str) -> None:
    console.print(f"  [dim]{message}[/dim]")


def print_error(message: str) -> None:
    console.print(f"\n[bold red]Error:[/bold red] {message}\n")


def print_warning(message: str) -> None:
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def print_done(tab_name: str) -> None:
    console.print(f"  [green]✓[/green] {tab_name} sheet updated.")
