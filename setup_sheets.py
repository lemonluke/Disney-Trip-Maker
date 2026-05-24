"""
One-time Google Sheets setup script.
Run this before using the planner: python setup_sheets.py
"""

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

SHEET_ID       = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Colour palette ─────────────────────────────────────────────────────────────
def rgb(r, g, b):
    return {"red": r / 255, "green": g / 255, "blue": b / 255}

# Layout colours
TITLE_BG   = rgb(26,  82, 118)
TITLE_FG   = rgb(255, 255, 255)
SECTION_BG = rgb(213, 232, 243)
SECTION_FG = rgb(30,  30,  30)
AUTO_BG    = rgb(248, 249, 250)
INPUT_BG   = rgb(255, 253, 231)

# Traffic light — backgrounds
CF_GREEN_BG  = rgb(198, 239, 206)   # Value / Open / good
CF_YELLOW_BG = rgb(255, 235, 156)   # Moderate / opens soon / caution
CF_RED_BG    = rgb(255, 199, 206)   # Peak / urgent
CF_BLUE_BG   = rgb(189, 215, 238)   # Day-of / informational
CF_PURPLE_BG = rgb(220, 213, 255)   # Available any time
CF_GOLD_BG   = rgb(255, 242, 204)   # Premier hotel / highlight
CF_GREY_BG   = rgb(242, 242, 242)   # No data / dim

# Traffic light — text colours (dark, for readability on light backgrounds)
CF_GREEN_FG  = rgb(0,   97,  0)
CF_YELLOW_FG = rgb(130, 80,  0)
CF_RED_FG    = rgb(156,  0,  6)
CF_BLUE_FG   = rgb(0,   70, 127)
CF_PURPLE_FG = rgb(80,   0,  80)
CF_GOLD_FG   = rgb(124, 81,  0)
CF_GREY_FG   = rgb(160, 160, 160)


# ── Helpers ────────────────────────────────────────────────────────────────────
def cell_range(sid, r1, c1, r2, c2):
    return {"sheetId": sid, "startRowIndex": r1, "endRowIndex": r2,
            "startColumnIndex": c1, "endColumnIndex": c2}

def bg_format(sid, r1, c1, r2, c2, bg, fg=None, bold=False):
    fmt = {"backgroundColor": bg}
    if fg or bold:
        fmt["textFormat"] = {}
        if fg:   fmt["textFormat"]["foregroundColor"] = fg
        if bold: fmt["textFormat"]["bold"] = True
    fields = "userEnteredFormat(backgroundColor" + (",textFormat" if fg or bold else "") + ")"
    return {"repeatCell": {"range": cell_range(sid, r1, c1, r2, c2),
                           "cell": {"userEnteredFormat": fmt}, "fields": fields}}

def col_width(sid, col, px):
    return {"updateDimensionProperties": {
        "range": {"sheetId": sid, "dimension": "COLUMNS",
                  "startIndex": col, "endIndex": col + 1},
        "properties": {"pixelSize": px}, "fields": "pixelSize"}}

def freeze(sid, rows=0):
    return {"updateSheetProperties": {
        "properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": rows}},
        "fields": "gridProperties.frozenRowCount"}}

def cf_formula(sid, r1, c1, r2, c2, formula, bg, fg=None, bold=False, index=0):
    """Conditional format rule using a custom formula (for full-row coloring)."""
    fmt = {"backgroundColor": bg}
    if fg or bold:
        fmt["textFormat"] = {}
        if fg:   fmt["textFormat"]["foregroundColor"] = fg
        if bold: fmt["textFormat"]["bold"] = bold
    return {"addConditionalFormatRule": {
        "rule": {
            "ranges": [cell_range(sid, r1, c1, r2, c2)],
            "booleanRule": {
                "condition": {"type": "CUSTOM_FORMULA",
                              "values": [{"userEnteredValue": formula}]},
                "format": fmt,
            },
        },
        "index": index,
    }}

def cf_contains(sid, r1, c1, r2, c2, text, bg, fg=None, bold=False, index=0):
    """Conditional format rule using TEXT_CONTAINS (for cell-level coloring)."""
    fmt = {"backgroundColor": bg}
    if fg or bold:
        fmt["textFormat"] = {}
        if fg:   fmt["textFormat"]["foregroundColor"] = fg
        if bold: fmt["textFormat"]["bold"] = bold
    return {"addConditionalFormatRule": {
        "rule": {
            "ranges": [cell_range(sid, r1, c1, r2, c2)],
            "booleanRule": {
                "condition": {"type": "TEXT_CONTAINS",
                              "values": [{"userEnteredValue": text}]},
                "format": fmt,
            },
        },
        "index": index,
    }}

def cf_eq(sid, r1, c1, r2, c2, text, bg, fg=None, bold=False, index=0):
    """Conditional format rule using TEXT_EQ."""
    fmt = {"backgroundColor": bg}
    if fg or bold:
        fmt["textFormat"] = {}
        if fg:   fmt["textFormat"]["foregroundColor"] = fg
        if bold: fmt["textFormat"]["bold"] = bold
    return {"addConditionalFormatRule": {
        "rule": {
            "ranges": [cell_range(sid, r1, c1, r2, c2)],
            "booleanRule": {
                "condition": {"type": "TEXT_EQ",
                              "values": [{"userEnteredValue": text}]},
                "format": fmt,
            },
        },
        "index": index,
    }}


# ── Connect ────────────────────────────────────────────────────────────────────
def connect():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(SHEET_ID)


# ── Inputs sheet ───────────────────────────────────────────────────────────────
def setup_inputs(spreadsheet):
    ws = spreadsheet.worksheet("Inputs")
    ws.clear()
    sid = ws.id

    content = [
        ["DISNEY TRIP PLANNER",         "",  ""],
        ["",                            "",  ""],
        ["Mode",                        "",  ""],
        ["Origin Airport",              "",  "3-letter airport code e.g. PHL, JFK, ORD"],
        ["Number of Travelers",         "",  "Leave blank to default to 1"],
        ["",                            "",  ""],
        ["MONTH / YEAR",                "",  ""],
        ["Month + Year",                "",  "e.g. 12/2026"],
        ["",                            "",  ""],
        ["SPECIFIC DATES",              "",  ""],
        ["Arrival Date",                "",  "e.g. 12/01/2026"],
        ["Departure Date",              "",  "e.g. 12/14/2026"],
        ["",                            "",  ""],
        ["PARK TIME",                   "",  ""],
        ["Disney Days",                 "",  ""],
        ["Universal Days",              "",  ""],
        ["",                            "",  ""],
        ["PHASE SPLIT",                 "",  ""],
        ["Phase 1 — Disney nights",     "",  "Auto-filled from Disney Days"],
        ["Phase 2 — Universal nights",  "",  "Auto-filled from Universal Days"],
        ["",                            "",  ""],
        ["STATUS",                      "",  ""],
        ["Mode selected",               "",  ""],
        ["Input status",                "",  ""],
        ["Last run",                    "",  ""],
        ["",                            "",  ""],
        ["EARLIEST BOOKING DATES",      "Earliest Date", "Status"],
        ["American Airlines flights",   "",  ""],
        ["Disney Resort hotels",        "",  ""],
        ["Universal on-site hotels",    "",  ""],
        ["Off-site hotels",             "",  ""],
        ["Disney park tickets",         "",  ""],
        ["Lightning Lane Multi Pass",   "",  ""],
        ["Lightning Lane Single Pass",  "",  ""],
        ["Universal park tickets",      "",  ""],
        ["Universal Express Pass",      "",  ""],
        ["Disney dining reservations",  "",  ""],
    ]
    ws.update("A1:C37", content)

    section_rows = [6, 9, 13, 17, 21, 26]

    requests = [
        col_width(sid, 0, 240), col_width(sid, 1, 180), col_width(sid, 2, 320),
        bg_format(sid, 0, 0, 1, 3, TITLE_BG, TITLE_FG, bold=True),
        *[bg_format(sid, r, 0, r + 1, 3, SECTION_BG, SECTION_FG, bold=True) for r in section_rows],
        bg_format(sid, 2, 1, 5, 2, INPUT_BG),
        bg_format(sid, 7, 1, 8, 2, INPUT_BG),
        bg_format(sid, 10, 1, 12, 2, INPUT_BG),
        bg_format(sid, 14, 1, 16, 2, INPUT_BG),
        bg_format(sid, 18, 1, 20, 2, INPUT_BG),
        bg_format(sid, 22, 1, 25, 3, AUTO_BG),
        bg_format(sid, 27, 1, 37, 3, AUTO_BG),
        # Hint text italic grey
        *[{"repeatCell": {
            "range": cell_range(sid, r, 2, r + 1, 3),
            "cell": {"userEnteredFormat": {"textFormat": {
                "italic": True, "foregroundColor": rgb(120, 120, 120)}}},
            "fields": "userEnteredFormat.textFormat"}}
          for r in [3, 4, 7, 10, 11, 18, 19]],
        # Dropdown
        {"setDataValidation": {
            "range": cell_range(sid, 2, 1, 3, 2),
            "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
                {"userEnteredValue": "Explore"},
                {"userEnteredValue": "Month View"},
                {"userEnteredValue": "Full Plan"},
            ]}, "showCustomUi": True, "strict": True}}},
        freeze(sid, rows=1),

        # ── Booking status column C (rows 28-37, 0-indexed 27-36) ─────────────
        # Priority order: most specific first (added last = highest priority)
        # "Opens in" — yellow (added first, lowest priority among CF rules)
        cf_contains(sid, 27, 2, 37, 3, "Opens in",        CF_YELLOW_BG, CF_YELLOW_FG),
        # "Day-of" — blue
        cf_contains(sid, 27, 2, 37, 3, "Day-of",          CF_BLUE_BG,   CF_BLUE_FG),
        # "Available any time" — lavender
        cf_contains(sid, 27, 2, 37, 3, "Available any",   CF_PURPLE_BG, CF_PURPLE_FG),
        # "OPENS TODAY" — bold green (higher priority, added later)
        cf_contains(sid, 27, 2, 37, 3, "OPENS TODAY",     CF_GREEN_BG,  CF_GREEN_FG, bold=True),
        # "OPEN — book now" — green (highest priority)
        cf_contains(sid, 27, 2, 37, 3, "OPEN",            CF_GREEN_BG,  CF_GREEN_FG),

        # ── Input status cell B24 (0-indexed row 23) ──────────────────────────
        cf_contains(sid, 23, 1, 24, 2, "Done",   CF_GREEN_BG,  CF_GREEN_FG),
        cf_contains(sid, 23, 1, 24, 2, "Running",CF_YELLOW_BG, CF_YELLOW_FG),
        cf_contains(sid, 23, 1, 24, 2, "Error",  CF_RED_BG,    CF_RED_FG),
        cf_contains(sid, 23, 1, 24, 2, "required",CF_RED_BG,   CF_RED_FG),
        cf_contains(sid, 23, 1, 24, 2, "conflict",CF_RED_BG,   CF_RED_FG),
    ]

    spreadsheet.batch_update({"requests": requests})
    print("  Inputs sheet configured.")


# ── 1 - Explore sheet ─────────────────────────────────────────────────────────
def setup_explore(spreadsheet):
    ws = spreadsheet.worksheet("1 - Explore")
    ws.clear()
    sid = ws.id
    ws.update("A1:K3", [
        ["24-Month Price Overview", "", "", "", "", "", "", "", "", "", ""],
        ["Month", "Season", "Avg Flight (pp)", "Avg Hotel/night", "Parks (pp)",
         "Est. Trip Total (pp)", "Notes", "Weather", "EPCOT Festival",
         "After-Hours Events", "Planning Tip"],
        ["~ = estimated (airline seats not yet on sale for this date)", "", "", "", "", "", "", "", "", "", ""],
    ])

    # Data rows 4-27 (0-indexed 3-27), all 11 columns A-K
    DATA = (3, 0, 27, 11)

    requests = [
        col_width(sid, 0, 120), col_width(sid, 1, 110), col_width(sid, 2, 150),
        col_width(sid, 3, 150), col_width(sid, 4, 110), col_width(sid, 5, 180),
        col_width(sid, 6, 280),
        col_width(sid, 7, 220),   # Weather
        col_width(sid, 8, 230),   # EPCOT Festival
        col_width(sid, 9, 280),   # After-Hours Events
        col_width(sid, 10, 420),  # Planning Tip
        bg_format(sid, 0, 0, 1, 11, TITLE_BG, TITLE_FG, bold=True),
        bg_format(sid, 1, 0, 2, 11, SECTION_BG, SECTION_FG, bold=True),
        # Legend row — italic grey
        {"repeatCell": {
            "range": cell_range(sid, 2, 0, 3, 11),
            "cell": {"userEnteredFormat": {"textFormat": {
                "italic": True, "foregroundColor": rgb(120, 120, 120)}}},
            "fields": "userEnteredFormat.textFormat"}},
        freeze(sid, rows=3),

        # ── Season row colouring (full row, based on column B) ────────────────
        # Peak — red  (added first = lowest CF priority)
        cf_formula(sid, *DATA, '=$B3="Peak"',     CF_RED_BG,    CF_RED_FG),
        # Moderate — yellow
        cf_formula(sid, *DATA, '=$B3="Moderate"', CF_YELLOW_BG, CF_YELLOW_FG),
        # Value — green (added last = highest CF priority)
        cf_formula(sid, *DATA, '=$B3="Value"',    CF_GREEN_BG,  CF_GREEN_FG),

        # ── "No data" cells — grey dim text ───────────────────────────────────
        cf_eq(sid,  2, 2, 26, 3, "No data", CF_GREY_BG, CF_GREY_FG),   # flight col
        cf_eq(sid,  2, 5, 26, 6, "No data", CF_GREY_BG, CF_GREY_FG),   # total col

        # ── Notes column G — red/yellow for known high-demand labels ──────────
        cf_contains(sid, 2, 6, 26, 7, "peak",          CF_RED_BG,    CF_RED_FG),
        cf_contains(sid, 2, 6, 26, 7, "Christmas",     CF_RED_BG,    CF_RED_FG),
        cf_contains(sid, 2, 6, 26, 7, "Thanksgiving",  CF_YELLOW_BG, CF_YELLOW_FG),
        cf_contains(sid, 2, 6, 26, 7, "Spring Break",  CF_YELLOW_BG, CF_YELLOW_FG),

        # ── After-Hours Events column J — amber when events present ───────────
        cf_contains(sid, 3, 9, 27, 10, "MNSSHP",  CF_YELLOW_BG, CF_YELLOW_FG),
        cf_contains(sid, 3, 9, 27, 10, "MVMCP",   CF_YELLOW_BG, CF_YELLOW_FG),
    ]

    spreadsheet.batch_update({"requests": requests})
    print("  1 - Explore sheet configured.")


# ── 2 - Month View sheet ──────────────────────────────────────────────────────
def setup_month_view(spreadsheet):
    ws = spreadsheet.worksheet("2 - Month View")
    ws.clear()
    sid = ws.id
    ws.update("A1:G2", [
        ["Month View", "", "", "", "", "", ""],
        ["Week", "Dates", "Cheapest flight day", "Priciest flight day",
         "Avg flight (pp)", "Avg hotel/night", "Notes"],
    ])

    # Data rows 3-6 (0-indexed 2-6), 7 columns
    DATA = (2, 0, 6, 7)

    requests = [
        col_width(sid, 0, 180), col_width(sid, 1, 160), col_width(sid, 2, 160),
        col_width(sid, 3, 160), col_width(sid, 4, 150), col_width(sid, 5, 150),
        col_width(sid, 6, 360),
        bg_format(sid, 0, 0, 1, 7, TITLE_BG, TITLE_FG, bold=True),
        bg_format(sid, 1, 0, 2, 7, SECTION_BG, SECTION_FG, bold=True),
        freeze(sid, rows=2),

        # ── Week row colouring based on Notes column (G) ──────────────────────
        # Christmas / peak — red
        cf_formula(sid, *DATA, '=ISNUMBER(SEARCH("Christmas",$G3))', CF_RED_BG,    CF_RED_FG),
        cf_formula(sid, *DATA, '=ISNUMBER(SEARCH("peak",$G3))',       CF_RED_BG,    CF_RED_FG),
        # Thanksgiving / Spring Break — yellow
        cf_formula(sid, *DATA, '=ISNUMBER(SEARCH("Thanksgiving",$G3))',CF_YELLOW_BG,CF_YELLOW_FG),
        cf_formula(sid, *DATA, '=ISNUMBER(SEARCH("Spring Break",$G3))',CF_YELLOW_BG,CF_YELLOW_FG),
        # Rows with no note and cheapest flight — green
        cf_formula(sid, *DATA, '=AND($G3="",$E3=MIN($E$3:$E$6))',      CF_GREEN_BG, CF_GREEN_FG),

        # ── "No data" cells — grey ────────────────────────────────────────────
        cf_eq(sid, 2, 4, 6, 5, "No data", CF_GREY_BG, CF_GREY_FG),

        # ── Section header rows — any row where col A starts with "──" ────────
        cf_formula(sid, 0, 0, 60, 7, '=LEFT($A1,1)="─"', SECTION_BG, SECTION_FG, bold=True),

        # ── Booking/Season section — status column E (index 4) ───────────────
        cf_contains(sid, 8, 4, 60, 5, "OPEN",         CF_GREEN_BG,  CF_GREEN_FG),
        cf_contains(sid, 8, 4, 60, 5, "Opens in",     CF_YELLOW_BG, CF_YELLOW_FG),
        cf_contains(sid, 8, 4, 60, 5, "Day-of",       CF_BLUE_BG,   CF_BLUE_FG),
        cf_contains(sid, 8, 4, 60, 5, "Available any",CF_PURPLE_BG, CF_PURPLE_FG),
    ]

    spreadsheet.batch_update({"requests": requests})
    print("  2 - Month View sheet configured.")


# ── 3 - Full Plan sheet ───────────────────────────────────────────────────────
def setup_full_plan(spreadsheet):
    ws = spreadsheet.worksheet("3 - Full Plan")
    ws.clear()
    sid = ws.id
    ws.update("A1", [["Full Trip Plan — fill in your dates on the Inputs sheet and run the script."]])

    # Large range covering the whole sheet
    ALL = (0, 0, 500, 10)

    requests = [
        col_width(sid, 0, 280), col_width(sid, 1, 200), col_width(sid, 2, 160),
        col_width(sid, 3, 160), col_width(sid, 4, 200), col_width(sid, 5, 160),
        col_width(sid, 6, 160), col_width(sid, 7, 160), col_width(sid, 8, 160),
        col_width(sid, 9, 320),
        bg_format(sid, 0, 0, 1, 10, TITLE_BG, TITLE_FG, bold=True),

        # ── Section header rows — any row where col A starts with "──" ────────
        cf_formula(sid, *ALL, '=LEFT($A1,1)="─"', SECTION_BG, SECTION_FG, bold=True),

        # ── Cost summary rows — bold GRAND TOTAL ─────────────────────────────
        cf_formula(sid, *ALL, '=$A1="GRAND TOTAL"', CF_GREEN_BG, CF_GREEN_FG, bold=True),

        # ── Hotels — Premier tier (col B contains "Premier") → gold ──────────
        cf_formula(sid, *ALL, '=ISNUMBER(SEARCH("Premier",$B1))', CF_GOLD_BG, CF_GOLD_FG),

        # ── Hotels — location tags ────────────────────────────────────────────
        # EPCOT / Inside EPCOT — light green (best Disney location for Phase 1)
        cf_formula(sid, *ALL, '=ISNUMBER(SEARCH("EPCOT",$B1))',   CF_GREEN_BG,  CF_GREEN_FG),

        # ── Rides — Single Pass (high demand, plan carefully) — red ──────────
        cf_formula(sid, *ALL, '=$D1="Single Pass"',  CF_RED_BG,    CF_RED_FG),
        # Multi Pass — yellow
        cf_formula(sid, *ALL, '=$D1="Multi Pass"',   CF_YELLOW_BG, CF_YELLOW_FG),

        # ── Express Pass — included (Premier hotel perk) — gold ──────────────
        cf_formula(sid, *ALL, '=$D1="Included"',     CF_GOLD_BG,   CF_GOLD_FG),
        # Express Pass — add-on available — blue
        cf_formula(sid, *ALL, '=$D1="Add-on"',       CF_BLUE_BG,   CF_BLUE_FG),

        # ── Booking window status column E (index 4) ──────────────────────────
        cf_contains(sid, 0, 4, 500, 5, "OPENS TODAY",  CF_GREEN_BG,  CF_GREEN_FG, bold=True),
        cf_contains(sid, 0, 4, 500, 5, "OPEN",         CF_GREEN_BG,  CF_GREEN_FG),
        cf_contains(sid, 0, 4, 500, 5, "Opens in",     CF_YELLOW_BG, CF_YELLOW_FG),
        cf_contains(sid, 0, 4, 500, 5, "Day-of",       CF_BLUE_BG,   CF_BLUE_FG),
        cf_contains(sid, 0, 4, 500, 5, "Available any",CF_PURPLE_BG, CF_PURPLE_FG),

        # ── Flight stops column E (index 4) — nonstop green ──────────────────
        cf_contains(sid, 0, 4, 500, 5, "Nonstop",      CF_GREEN_BG,  CF_GREEN_FG),
        cf_contains(sid, 0, 4, 500, 5, "1 stop",       CF_YELLOW_BG, CF_YELLOW_FG),
        cf_contains(sid, 0, 4, 500, 5, "2 stop",       CF_RED_BG,    CF_RED_FG),

        # ── Thrill level column B (index 1) in rides sections ────────────────
        cf_formula(sid, *ALL, '=$B1="Thrill"',   CF_RED_BG,    CF_RED_FG),
        cf_formula(sid, *ALL, '=$B1="Moderate"', CF_YELLOW_BG, CF_YELLOW_FG),
        cf_formula(sid, *ALL, '=$B1="Mild"',     CF_GREEN_BG,  CF_GREEN_FG),
    ]

    spreadsheet.batch_update({"requests": requests})
    print("  3 - Full Plan sheet configured.")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Connecting to Google Sheets...")
    spreadsheet = connect()
    print("Connected. Setting up sheets...\n")
    setup_inputs(spreadsheet)
    setup_explore(spreadsheet)
    setup_month_view(spreadsheet)
    setup_full_plan(spreadsheet)
    print("\nAll sheets configured.")
    print("Fill in the Inputs sheet, then run: python main.py")
