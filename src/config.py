import os
from dotenv import load_dotenv

load_dotenv()

# ── API credentials ────────────────────────────────────────────────────────────
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ── Destination ────────────────────────────────────────────────────────────────
DESTINATION_AIRPORT = "MCO"

# ── Date format ────────────────────────────────────────────────────────────────
DATE_FORMAT = "%m/%d/%Y"
MONTH_FORMAT = "%m/%Y"
DATE_FORMAT_API = "%Y-%m-%d"   # Serpapi requires YYYY-MM-DD regardless of user input format

# ── Flight search ──────────────────────────────────────────────────────────────
MAX_FLIGHT_RESULTS = 5

# ── Sheet tab names ────────────────────────────────────────────────────────────
TAB_INPUTS = "Inputs"
TAB_EXPLORE = "1 - Explore"
TAB_MONTH_VIEW = "2 - Month View"
TAB_FULL_PLAN = "3 - Full Plan"

# ── Mode values (as written in the dropdown) ───────────────────────────────────
MODE_EXPLORE = "Explore"
MODE_MONTH_VIEW = "Month View"
MODE_FULL_PLAN = "Full Plan"

# ── Inputs sheet cell references ───────────────────────────────────────────────
CELL_MODE = "B3"
CELL_ORIGIN = "B4"
CELL_TRAVELERS = "B5"
CELL_MONTH_YEAR = "B8"
CELL_ARRIVAL = "B11"
CELL_DEPARTURE = "B12"
CELL_DISNEY_DAYS = "B15"
CELL_UNIVERSAL_DAYS = "B16"
CELL_PHASE1_NIGHTS = "B19"
CELL_PHASE2_NIGHTS = "B20"

# ── Status rows (written by the script before any API calls) ───────────────────
CELL_STATUS_MODE = "B23"
CELL_STATUS_INPUT = "B24"
CELL_STATUS_LAST_RUN = "B25"

# ── Booking date rows on the Inputs sheet (rows 28–37) ────────────────────────
# Each tuple is (date cell, status cell)
BOOKING_CELLS = {
    "American Airlines flights":        ("B28", "C28"),
    "Disney Resort hotels":             ("B29", "C29"),
    "Universal on-site hotels":         ("B30", "C30"),
    "Off-site hotels":                  ("B31", "C31"),
    "Disney park tickets":              ("B32", "C32"),
    "Lightning Lane Multi Pass":        ("B33", "C33"),
    "Lightning Lane Single Pass":       ("B34", "C34"),
    "Universal park tickets":           ("B35", "C35"),
    "Universal Express Pass":           ("B36", "C36"),
    "Disney dining reservations":       ("B37", "C37"),
}

# ── Scraping targets (verify these URLs are still correct before each trip) ───
URL_DISNEY_TICKETS = "https://disneyworld.disney.go.com/admission/tickets/"
URL_UNIVERSAL_TICKETS = "https://www.universalorlando.com/web/en/us/tickets-passes/base-tickets"
URL_DISNEY_HOTELS = "https://disneyworld.disney.go.com/resorts/"
URL_UNIVERSAL_HOTELS = "https://www.universalorlando.com/web/en/us/hotels"

# ── Season definitions (month numbers) ────────────────────────────────────────
SEASONS = {
    "Value":    [1, 2, 9],
    "Moderate": [3, 4, 5, 8, 10, 11],
    "Peak":     [6, 7, 12],
}

# ── Known high-demand event months (for tagging in Mode 1 grid) ───────────────
HIGH_DEMAND_NOTES = {
    12: "Christmas / New Year — peak crowds and prices",
    6:  "Summer peak — school holidays begin",
    7:  "Summer peak — busiest month of the year",
    3:  "Spring Break — significant crowd spike mid-month",
    11: "Thanksgiving week — very busy final week",
}
