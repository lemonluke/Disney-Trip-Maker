# Disney Florida Trip Planner
### A Python + Google Sheets Automation Project

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [How It Works](#2-how-it-works)
3. [Free Resources & APIs](#3-free-resources--apis)
4. [Prerequisites](#4-prerequisites)
5. [Project Structure](#5-project-structure)
6. [Google Cloud Setup](#6-google-cloud-setup)
7. [Google Sheets Setup](#7-google-sheets-setup)
8. [Amadeus API Setup](#8-amadeus-api-setup)
9. [Environment Variables](#9-environment-variables)
10. [Module Breakdown](#10-module-breakdown)
11. [Running the Project](#11-running-the-project)
12. [Adding a Watch Loop](#12-adding-a-watch-loop)
13. [Deployment on PythonAnywhere (Optional)](#13-deployment-on-pythonanywhere-optional)
14. [Troubleshooting](#14-troubleshooting)
15. [Limitations & Notes](#15-limitations--notes)
16. [Two-Phase Trip Strategy](#two-phase-trip-strategy--context-for-the-code)
17. [Future Extension — Generalising Beyond Florida and Disney](#future-extension--generalising-beyond-florida-and-disney)

---

## 1. Project Overview

This project automates Disney Florida trip cost research. It works in three modes depending on how much you have decided:

- **Mode 1 — Explore:** Provide only your departure airport and get a 24-month price grid (from next month to two years out) showing average flight, hotel, and park costs per month, with season tags to help you find the best time to go
- **Mode 2 — Month View:** Add a month and year (without specific dates) and get a week-by-week price breakdown for that month, plus park info and booking window dates anchored to the 1st of the month
- **Mode 3 — Full Plan:** Add specific arrival and departure dates and get the complete trip planner: live flight search, hotel details with ratings and distances, park pricing, ride lists, Lightning Lane / Express Pass info, and a two-phase Disney + Universal cost breakdown

In all modes, number of travelers is optional and defaults to 1 if left blank. Origin airport is the only required field — the script will not run without it and tells you so clearly. Month/Year and specific dates can coexist as long as they are in the same calendar month.

Everything is **free to run** using free-tier APIs, free Google services, and web scraping where APIs are unavailable.

---

## 2. How It Works

The planner is built around a single Inputs sheet that acts as the hub. A dropdown at the top of that sheet lets you select which mode to run. The script reads the dropdown value, validates the relevant fields, runs only the pipeline for that mode, and writes results exclusively to that mode's sheet — the other two are left untouched.

```
Inputs Sheet
+----------------------------------+
| Mode: [ Explore / v ]            |  <- dropdown controls everything
| Origin Airport   [ JFK ]         |  <- always required
| Travelers        [ 4   ]         |  <- always optional, defaults to 1
|                                  |
| MODE 2 + 3 INPUTS                |  <- greyed out when not relevant
| Month + Year     [ 2026-12 ]     |
| Arrival Date     [ 2026-12-01 ]  |
| Departure Date   [ 2026-12-14 ]  |
| Disney Days      [ 10 ]          |
| Universal Days   [ 5  ]          |
|                                  |
| STATUS                           |
| Mode: Explore  |  Ready to run   |
| Last run: 17 May 2026  14:32     |
+----------------------------------+
         |
         | script reads dropdown + inputs
         v
+------------------+------------------+------------------+
|  1 - Explore     |  2 - Month View  |  3 - Full Plan   |
|  (overwritten    |  (untouched)     |  (untouched)     |
|   this run)      |                  |                  |
+------------------+------------------+------------------+
```

Only the sheet matching the selected mode is written to on any given run. The other two sheets keep whatever results they last produced, so you can freely compare outputs across modes without re-running everything.

---

### The Three Modes Explained

**Mode 1 — Explore (no dates needed)**
You have an airport but no dates. The script generates a 24-month price overview covering from next month up to two years from today. Each month shows average flight cost, average hotel cost, and a rough park total, so you can compare seasons and months before committing to anything. Travelers defaults to 1 if not filled in.

**Mode 2 — Month View (soft commitment)**
You know the month and year but have not picked specific dates. The script shows average prices for that month alongside a week-by-week breakdown so you can see how prices shift across the month. Booking window dates are calculated using the 1st of the chosen month as a conservative anchor. Travelers defaults to 1 if not filled in.

**Mode 3 — Full Plan (specific dates)**
Both arrival and departure dates are filled in. The script runs the complete trip planner: live flight search, hotel details, park pricing, ride lists, booking windows, and the two-phase Disney and Universal cost summary.

---

### Mode Coexistence Rules

Month and Year and specific dates can both be filled in at the same time as long as they do not conflict. The script validates this on every run regardless of which mode is selected:

| Combination | Valid? | Behaviour |
|---|---|---|
| Airport only | Yes | Mode 1 runs cleanly |
| Airport + Month/Year | Yes | Mode 2 runs cleanly |
| Airport + specific dates | Yes | Mode 3 runs cleanly |
| Airport + Month/Year + specific dates (same month) | Yes | Mode 3 runs; Month/Year shown as context |
| Airport + Month/Year + specific dates (different month) | No | Script stops and flags the conflict |
| No airport, any mode selected | No | Script stops with a clear error |

---

## 3. Free Resources & APIs

Every resource used in this project is **completely free**. Here is what you will use and why:

| Resource | Purpose | Free Tier Details |
|---|---|---|
| **Amadeus for Developers** | Flight search (American Airlines + all carriers to MCO) | 2,000 API calls/month free on test environment |
| **Google Sheets API** | Read inputs / write results to your spreadsheet | Free with a Google account |
| **Google Drive API** | Required alongside Sheets API for authentication | Free with a Google account |
| **gspread** (Python library) | Python wrapper to interact with Google Sheets | Free open-source library |
| **requests** (Python library) | HTTP requests for web scraping | Free open-source library |
| **BeautifulSoup4** (Python library) | Parse HTML from Disney/Universal/hotel sites | Free open-source library |
| **python-dotenv** (Python library) | Load API keys from a `.env` file safely | Free open-source library |
| **rich** (Python library) | Pretty terminal output while the script runs | Free open-source library |
| **PythonAnywhere** *(optional)* | Host and schedule the script in the cloud | Free hobby tier available |

> **Amadeus Note:** The free tier uses a **test environment** with simulated (but realistic) flight data. This is perfectly fine for planning and cost estimation. Real live data requires a paid production key.

---

## 4. Prerequisites

Before starting, make sure you have the following:

- **Python 3.9 or higher** installed on your machine
  - Check with: `python --version`
  - Download from: https://www.python.org/downloads
- **pip** (comes with Python)
  - Check with: `pip --version`
- **A Google Account** (for Google Sheets and Google Cloud)
- **A free Amadeus Developer account** (sign up at https://developers.amadeus.com)
- **A terminal / command prompt** you are comfortable using

### Install Required Python Libraries

Once Python is installed, run the following command in your terminal:

```bash
pip install gspread google-auth requests beautifulsoup4 python-dotenv rich amadeus
```

To confirm all libraries installed successfully, run:

```bash
pip show gspread amadeus beautifulsoup4
```

---

## 5. Project Structure

Create a folder on your computer called `disney_trip_planner`. Inside it, create the following files (all empty for now):

```
disney_trip_planner/
│
├── main.py               # Entry point — detects mode and runs the right pipeline
├── sheets.py             # All Google Sheets read/write logic
├── flights.py            # Fetches flight prices via Amadeus API (Mode 3)
├── price_explorer.py     # Builds price grids for Mode 1 and Mode 2
├── hotels.py             # Scrapes hotel details for Disney + Universal areas (Mode 3)
├── parks.py              # Scrapes Disney World + Universal admission, rides, fast passes
├── booking_windows.py    # Calculates earliest booking dates for all trip components
├── trip_strategy.py      # Splits the trip into Phase 1 (Disney) and Phase 2 (Universal)
├── report.py             # Prints a summary to the terminal
├── config.py             # Sheet ID, cell references, and constants
├── data/
│   ├── disney_rides.py   # Hardcoded ride list + Lightning Lane eligibility per park
│   └── universal_rides.py# Hardcoded ride list + Express Pass eligibility per park
├── .env                  # Your secret API keys (never share this file)
└── .gitignore            # Prevents .env from being accidentally uploaded
```

The `data/` folder holds reference data for rides and fast-pass options. These are maintained manually since neither Disney nor Universal provides a public API for ride data. They change infrequently (new rides open a few times per year at most) and are easy to keep up to date.

### Create your `.gitignore` file now

If you plan to use Git, add this to `.gitignore` immediately so you never accidentally expose your keys:

```
.env
credentials.json
__pycache__/
*.pyc
```

---

## 6. Google Cloud Setup

This section sets up authentication so your Python script can read and write to Google Sheets.

### Step 1 — Create a Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click the project dropdown at the top → **New Project**
3. Name it something like `disney-trip-planner`
4. Click **Create**

### Step 2 — Enable the Required APIs

With your new project selected:

1. In the left sidebar go to **APIs & Services → Library**
2. Search for **Google Sheets API** → click it → click **Enable**
3. Go back to the library, search for **Google Drive API** → click it → click **Enable**

### Step 3 — Create a Service Account

A service account is like a "bot user" that your script logs in as to access the sheet.

1. In the left sidebar go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → Service Account**
3. Give it a name like `trip-planner-bot`
4. Click **Create and Continue**
5. For the role, select **Editor** under Basic roles
6. Click **Done**

### Step 4 — Download the Credentials JSON Key

1. On the Credentials page, click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key → Create new key**
4. Choose **JSON** format → click **Create**
5. A file will download automatically — rename it to `credentials.json`
6. Move `credentials.json` into your `disney_trip_planner/` folder

> **Important:** This file contains your private credentials. Never share it, never commit it to GitHub. It is already covered by your `.gitignore` above.

---

## 7. Google Sheets Setup

### Step 1 — Create the Spreadsheet

1. Go to https://sheets.google.com
2. Create a new blank spreadsheet
3. Rename it to `Disney Trip Planner`

### Step 2 — Share It With Your Service Account

1. Open the `credentials.json` file in a text editor
2. Find the field called `"client_email"` — it will look like:
   `trip-planner-bot@disney-trip-planner.iam.gserviceaccount.com`
3. In your Google Sheet, click **Share** (top right)
4. Paste that email address in and give it **Editor** access
5. Uncheck "Notify people" and click **Share**

### Step 3 — Set Up the Sheet Layout

The spreadsheet has four sheets. Create them by clicking the + button at the bottom:

| Sheet Name | Purpose |
|---|---|
| `Inputs` | Hub sheet — mode dropdown, all input fields, status, booking dates |
| `1 - Explore` | Mode 1 output — 24-month price grid |
| `2 - Month View` | Mode 2 output — weekly breakdown and parks info |
| `3 - Full Plan` | Mode 3 output — flights, hotels, parks, booking windows, summary |

Each output sheet is only overwritten when its corresponding mode is selected and the script is run. The other two are always left as-is.

---

#### `Inputs` Sheet Layout

The Inputs sheet is designed to be readable at default zoom without horizontal scrolling. Labels sit in column A, values in column B, and status messages in column C. Columns beyond C are hidden. Rows below the last used row are hidden after the script runs.

The sheet is divided into four visual sections separated by a lightly shaded divider row:

**Section 1 — Mode Selection**

| Cell | Content | Notes |
|---|---|---|
| A1 | `DISNEY TRIP PLANNER` | Title row — merged across A1:C1, shaded |
| A3 | `Mode` | |
| B3 | Dropdown: `Explore / Month View / Full Plan` | Set via Data > Data Validation > Dropdown |
| A4 | `Origin Airport` | |
| B4 | User types here e.g. `JFK` | Required for all modes |
| A5 | `Number of Travelers` | |
| B5 | User types here e.g. `4` | Optional — defaults to 1 if blank |

**Section 2 — Mode Inputs** *(greyed out by conditional formatting when not relevant)*

| Cell | Content | Active when |
|---|---|---|
| A7 | `MONTH / YEAR` | Divider row |
| A8 | `Month + Year` | |
| B8 | User types e.g. `2026-12` | Mode 2 and Mode 3 |
| A10 | `SPECIFIC DATES` | Divider row |
| A11 | `Arrival Date` | |
| B11 | User types e.g. `2026-12-01` | Mode 3 only |
| A12 | `Departure Date` | |
| B12 | User types e.g. `2026-12-14` | Mode 3 only |
| A14 | `PARK TIME` | Divider row |
| A15 | `Disney Days` | |
| B15 | User types e.g. `10` | Mode 3 (optional) |
| A16 | `Universal Days` | |
| B16 | User types e.g. `5` | Mode 3 (optional) |
| A18 | `PHASE SPLIT` | Divider row |
| A19 | `Phase 1 — Disney nights` | |
| B19 | Auto-filled from Disney days, or enter manually | Mode 3 |
| A20 | `Phase 2 — Universal nights` | |
| B20 | Auto-filled from Universal days, or enter manually | Mode 3 |

**Section 3 — Status** *(always auto-filled by the script)*

| Cell | Content |
|---|---|
| A22 | `STATUS` — divider row |
| A23 | `Mode selected` |
| B23 | e.g. `Explore` |
| A24 | `Input status` |
| B24 | e.g. `Ready to run` or a plain-English error message |
| A25 | `Last run` |
| B25 | e.g. `17 May 2026  14:32` |

**Section 4 — Booking Dates** *(auto-filled in Mode 2 and Mode 3 only)*

| Cell | Content |
|---|---|
| A27 | `EARLIEST BOOKING DATES` — divider row |
| A28 | `American Airlines flights` |
| A29 | `Disney Resort hotels` |
| A30 | `Universal on-site hotels` |
| A31 | `Off-site hotels` |
| A32 | `Disney park tickets` |
| A33 | `Lightning Lane Multi Pass` |
| A34 | `Lightning Lane Single Pass` |
| A35 | `Universal park tickets` |
| A36 | `Universal Express Pass` |
| A37 | `Disney dining reservations` |

Column B (rows 28–37) holds the calculated earliest booking date. Column C holds the status label (`Opens in X days`, `OPEN — book now`, etc.).

---

#### Setting Up the Mode Dropdown

1. Click cell B3
2. Go to **Data > Data Validation**
3. Under Criteria select **Dropdown (from a list)**
4. Enter the three options: `Explore`, `Month View`, `Full Plan`
5. Click **Save**

The cell will now show a dropdown arrow. The script reads this cell's value on every run to determine which mode to execute.

---

#### Setting Up Conditional Formatting for Greyed Fields

Cells that are not relevant to the selected mode should be visually muted so the sheet only shows what matters. Do this with conditional formatting:

1. Select the cells for Mode 3 only fields (B11, B12, B15, B16, B19, B20)
2. Go to **Format > Conditional Formatting**
3. Under Format rules select **Custom formula is**
4. Enter: `=$B$3<>"Full Plan"`
5. Set the formatting style to light grey text on a light grey background
6. Click **Done**

Repeat for Mode 2 and Mode 3 fields (B8):
- Formula: `=$B$3="Explore"` — grey out B8 when Explore is selected

This means when a user selects Explore from the dropdown, all date and phase fields fade out automatically. When they switch to Full Plan, they become active again. The script also ignores greyed fields when reading inputs, so a value accidentally left in a greyed cell will not affect the run.

---

#### Hiding Unused Columns and Rows

After the script runs it calls `sheets.py` to hide columns beyond C on the Inputs sheet and any rows below the last populated row. You can also do this manually:

- Right-click any column header beyond C and select **Hide column**
- Select the empty rows below row 37, right-click, and select **Hide rows**

The output sheets (1 - Explore, 2 - Month View, 3 - Full Plan) follow the same principle — the script hides unused columns and rows after writing results so the sheet feels contained without wasted space.

---

---

#### `1 - Explore` Sheet Layout *(Mode 1 output)*

---

#### Transition Day Logic

There are 3 days that do not belong cleanly to either park phase:

| Day | Description | Counted as |
|---|---|---|
| **Arrival day** | You fly in and check in to your Disney resort. Unlikely to do a full park day. | Disney day 1 — hotel night counted in Phase 1 |
| **Switch day** | You check out of Disney, check in to Universal. Travel between resorts takes part of the day. | Counted in both park-day totals as a shared transition — only 1 hotel night charged (Universal Phase 2 check-in night) |
| **Departure day** | You check out and fly home. No full park day. | Universal final day — hotel night is the night before, already counted in Phase 2 |

**How park days convert to hotel nights:**

```
Disney hotel nights  = Disney days - 1
                       (arrival day counts as day 1 but the night before it is not charged)

Universal hotel nights = Universal days - 1
                         (departure day is the last day but you check out that morning)

Switch day           = 1 night charged to Universal (you sleep at Universal that night)

Total hotel nights   = (Disney days - 1) + (Universal days - 1)
                     = Disney days + Universal days - 2
```

**Example:** 10 Disney days + 5 Universal days
- Disney hotel nights: 9
- Universal hotel nights: 4
- Total hotel nights: 13
- Switch day is Universal night 1 (already included in the 4 Universal nights)

The script performs this calculation automatically when Disney days and Universal days are filled in and writes the resulting nights into the Phase 1 and Phase 2 rows. If you prefer to enter nights directly, leave the park days cells blank and fill in the phase nights manually.

**Validation rules for park days:**

| Scenario | Behaviour |
|---|---|
| Both park days blank | Phase nights used as-is if filled in manually; no calculation performed |
| Disney days only | Phase 1 nights calculated; Phase 2 nights left for manual entry |
| Universal days only | Phase 2 nights calculated; Phase 1 nights left for manual entry |
| Both park days filled | Both phase nights calculated and auto-filled |
| Park days given + specific dates: total nights don't match | Script warns in B16: `Park days total (X nights) does not match trip length (Y nights). Check your inputs.` but does not stop — lets you decide which to trust |
| Park days given, no specific dates (Mode 1 or 2) | Days stored and used to personalise the price estimates (e.g. adjusting hotel night count in the reference calculation) |

---

The script writes the selected mode to B23 and the status to B24 on every run before doing anything else. If there is a problem it writes a plain-English message and stops.

| Scenario | B23 (Mode) | B24 (Status) | Action |
|---|---|---|---|
| No airport | — | `Origin airport is required. Please fill in cell B4.` | Stops immediately |
| Explore selected, airport present | `Explore` | `Ready — generating 24-month price overview` | Runs Mode 1 |
| Month View selected, Month/Year present | `Month View` | `Ready — showing prices for 2026-12` | Runs Mode 2 |
| Month View selected, no Month/Year | `Month View` | `Month + Year is required for Month View. Please fill in cell B8.` | Stops |
| Full Plan selected, full dates present | `Full Plan` | `Ready — full trip plan for Dec 1-14` | Runs Mode 3 |
| Full Plan selected, arrival but no departure | `Full Plan` | `Departure date is required when arrival date is filled in.` | Stops |
| Month/Year and dates filled (same month) | current mode | `Ready — Month/Year matches arrival date` | Runs normally |
| Month/Year and dates filled (different month) | `Conflict` | `Month/Year (2026-11) conflicts with arrival date (2026-12-01). Please correct.` | Stops |
| Park days imply different total than trip length | current mode | `Warning — park days imply X nights but trip is Y nights. Proceeding with specific dates.` | Runs with warning |
| Travelers blank | current mode | Proceeds normally | Defaults to 1, noted in terminal |

---

#### `Price Explorer` Tab Layout *(Mode 1 only — renamed to 1 - Explore)*

See the `1 - Explore` sheet layout in the section above.

---

#### `3 - Full Plan` Sheet Layout *(Mode 3 output)*

Mode 3 has the most data. Rather than squeezing it all into one sheet, `3 - Full Plan` is structured as a landing sheet with a summary at the top, followed by scrollable sections for flights, hotels, parks, and booking windows below — each separated by a shaded divider row. This keeps everything in one place while remaining navigable without needing additional sub-tabs.

**Top section — trip summary:**

| Column | Content |
|---|---|
| A | Category label |
| B | Value |
| C | Per person |

Rows cover: Phase 1 subtotal (flights outbound + Disney hotels + Disney parks), Phase 2 subtotal (Universal hotels + Universal parks), flights return, grand total, and per-person total.

**Flights section:**

| Column | Content |
|---|---|
| A | Flight option number |
| B | Departure time |
| C | Arrival time |
| D | Airline / flight number |
| E | Price per person |
| F | Total (all travelers) |

**Hotels — Disney section:**

| Column | Content |
|---|---|
| A | Hotel name |
| B | Location tag (e.g. `Inside EPCOT`, `Disney Resort — Magic Kingdom Area`, `1.2 miles from Animal Kingdom`) |
| C | Star rating |
| D | Price per night |
| E | Phase 1 total |
| F | Distance to Magic Kingdom |
| G | Distance to EPCOT |
| H | Distance to Hollywood Studios |
| I | Distance to Animal Kingdom |
| J | On-site perks (e.g. Early Park Entry, Skyliner access, Lightning Lane discount) |

**Hotels — Universal section:**

| Column | Content |
|---|---|
| A | Hotel name |
| B | Location tag (e.g. `On-site Universal — Premier`, `0.3 miles from Universal Studios`) |
| C | Star rating |
| D | Price per night |
| E | Phase 2 total |
| F | Distance to Universal Studios Florida |
| G | Distance to Islands of Adventure |
| H | Distance to Epic Universe |
| I | On-site perks (e.g. Express Pass included, Early park entry, Water taxi to parks) |

**Parks — Disney section:**

Each of the four Disney parks (Magic Kingdom, EPCOT, Hollywood Studios, Animal Kingdom) gets a row group with a bold header. The group contains ticket pricing rows followed by the ride list for that park.

| Column | Content |
|---|---|
| A | Park name (header row) or ride name |
| B | Ticket type or thrill level (Mild / Moderate / Thrill) |
| C | Price per person or height requirement |
| D | Total (all travelers) or Lightning Lane type (Multi Pass / Single Pass / None) |
| E | Notes (e.g. typically long wait, fan favourite, virtual queue required) |

**Parks — Universal section:**

Same structure as the Disney parks section but for Universal Studios Florida, Islands of Adventure, and Epic Universe. Lightning Lane column uses Express Pass terminology (Included with Premier hotel / Add-on / None).

**Booking Windows section:**

| Column | Content |
|---|---|
| A | Category |
| B | Item name |
| C | Booking window rule |
| D | Earliest booking date |
| E | Days until open |
| F | Status (Open / Opens in X days / Available any time / Day-of only) |
| G | Notes |
| H | Booking URL |

---

---

#### `Booking Windows` Tab Layout

This tab is the full detail view of every booking window. The `Inputs` tab shows the summary dates at a glance; this tab gives you the complete picture including rules, notes, and direct booking links.

| Column | Content |
|---|---|
| A | Category *(Flights / Hotels / Parks / Dining / Fast Pass)* |
| B | Item Name *(e.g. `American Airlines`, `Disney Resort Hotels`, `Lightning Lane Single Pass`)* |
| C | Booking Window Rule *(e.g. `Opens 500 days before check-in`, `Opens 60 days before park date`)* |
| D | Earliest Booking Date *(calculated from your arrival date)* |
| E | Days Until Open *(countdown from today — updates every time you run the script)* |
| F | Status *(`OPEN — book now` / `Opens in X days` / `Not yet announced`)* |
| G | Notes *(caveats, tips, or conditions — see below)* |
| H | Booking URL *(direct link to the booking page)* |

**Booking windows tracked (current rules as of project build — verify before your trip):**

| Item | Window Rule | Notes |
|---|---|---|
| American Airlines flights | ~331 days before departure | AA opens booking exactly 331 days out. Set a reminder for this date. |
| Disney Resort hotels | Up to 499 days before check-in (for Disney Vacation Club) / ~500 days for general public via Disney direct | Book early — EPCOT-area resorts sell out fast for peak dates |
| Universal on-site hotels (Premier) | Typically 12 months out | No strict cutoff but inventory is limited |
| Off-site hotels | Varies by property — typically 12 months, some as early as 18 months | Flexible cancellation off-site gives more room to rebook |
| Disney park tickets | Can be purchased any time in advance; no hard window | Prices increase closer to date — buy early to lock in lower price |
| Disney Lightning Lane Multi Pass | Opens at 7:00am on the day of your park visit (on-site guests) or day-of (off-site) | Cannot be pre-booked — this is a day-of purchase only |
| Disney Lightning Lane Single Pass | Opens 7:00am on the day of your park visit | Day-of only; most in-demand rides (Tiana's, Cosmic Rewind) sell out within minutes |
| Universal park tickets | No hard advance booking window; purchase any time | Prices do not vary by purchase date the way Disney's do |
| Universal Express Pass | Purchase any time in advance; included with Premier hotel | If buying separately, no urgency — inventory is not scarce |
| Disney dining reservations | Opens 60 days before your dining date (on-site guests get a slight priority window) | Most popular restaurants (Be Our Guest, Space 220, Ohana) book up within hours of opening |
| Disney Genie+ / My Disney Experience | Replaced by Lightning Lane — no pre-booking | Plan your Lightning Lane strategy before arrival using the ride list in `Parks - Disney` |

> **Booking window rules change.** Disney in particular adjusts its policies periodically. The rules above are stored in `booking_windows.py` as a hardcoded dictionary so you can update them easily in one place without touching other modules. Each entry has a source URL so you can verify the current rule before your trip.

---

### Step 4 — Copy Your Sheet ID

The Sheet ID is in the URL when you have the sheet open:

```
https://docs.google.com/spreadsheets/d/THIS_PART_HERE/edit
```

Copy the long string between `/d/` and `/edit` — you will need it in the next step.

---

## 8. Amadeus API Setup

Amadeus provides a free flight search API that includes American Airlines routes.

### Step 1 — Create an Account

1. Go to https://developers.amadeus.com
2. Click **Register** and create a free account
3. Verify your email address

### Step 2 — Create an App

1. Once logged in, go to **My Apps** in the top menu
2. Click **Create new app**
3. Name it `Disney Trip Planner`
4. Click **Create**

### Step 3 — Get Your API Keys

After creating the app you will see:

- **API Key** (also called Client ID)
- **API Secret** (also called Client Secret)

Copy both of these — you will add them to your `.env` file next.

> **Note:** By default your app is in the **Test environment**, which uses simulated data. This is free and has no time limit. It is sufficient for trip planning purposes.

---

## 9. Environment Variables

Your `.env` file stores all secrets and configuration. It should look like this:

```env
# Amadeus API
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here

# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

Replace the placeholder values with your real keys. Save the file. This file is read by `python-dotenv` at runtime and is never shared or uploaded anywhere.

---

## 10. Module Breakdown

Here is what each file in the project will do. This section gives you a clear understanding of the responsibility of each module before you write any code.

---

### `config.py`
Loads environment variables and defines constants used across the project such as:
- Tab names and cell addresses for each input and output section in the sheet
- The destination airport code (`MCO` for Orlando)
- Date format strings
- Number of flight results to return
- URL targets for scraping
- Reference to the `BOOKING_WINDOWS` dictionary in `booking_windows.py`

---

### `sheets.py`
Handles all communication with Google Sheets using `gspread`. Responsible for:
- Authenticating with the service account credentials
- Opening the spreadsheet by its ID
- Reading the input cells (origin, arrival date, departure date, travelers, phase split nights)
- Writing rows of flight data to the Flights tab
- Writing rows of hotel data to the Hotels tabs
- Writing rows of park data to the Parks tabs
- Writing booking window summary rows to the Inputs tab (rows 12–21)
- Writing the full booking window detail table to the Booking Windows tab
- Writing the summary totals to the Summary tab
- Clearing old results before writing new ones so stale data never shows

---

### `price_explorer.py`
Handles all price estimation logic for Mode 1 and Mode 2. Responsible for:

**Mode 1 — 24-month grid:**
- Calculating the 24 calendar months starting from the month after today
- For each month, making a small number of targeted Amadeus API calls (2–3 sample dates per month) to get representative flight prices to MCO from the origin airport
- Averaging those sample prices to produce a monthly estimate
- Scraping or estimating hotel mid-range nightly costs for each month (using known seasonal pricing patterns as a baseline when live scraping is unavailable)
- Applying static park ticket prices (consistent year-round with noted peak exceptions)
- Calculating an estimated 7-night trip total per month per person as the reference cost
- Tagging each month with a season label and any notable events or surcharges
- Returning a 24-row dataset ready to write to the `Price Explorer` tab

**Mode 2 — week-by-week breakdown:**
- Accepting the chosen month and year from the Inputs tab
- Splitting the month into weekly windows (Week 1, Week 2, etc.)
- Querying Amadeus for flight prices on several dates within each week
- Identifying the cheapest and most expensive individual days in each week
- Calculating the week's average hotel cost and comparing it to the monthly average
- Flagging weeks with known events, school holidays, or price spikes
- Returning a per-week dataset ready to write to the `Month Breakdown` tab

**Amadeus API call management:**
The free tier allows 2,000 calls per month. Mode 1 makes approximately 48–72 calls (2–3 per month × 24 months). Mode 2 makes approximately 12–20 calls (3–5 per week × 4 weeks). Both are well within the free limit, but `price_explorer.py` includes a small delay between calls (`time.sleep(0.5)`) to avoid rate limiting and logs how many calls were made so you can track usage.

> **Estimate accuracy:** Mode 1 prices are averages across a small sample and are best used for relative comparison (i.e. "December is more expensive than September") rather than precise budgeting. Mode 3 with specific dates gives the most accurate numbers.

---

### `flights.py`
Uses the **Amadeus Python SDK** to search for flights. Responsible for:
- Accepting the origin airport code, travel dates, and number of travelers
- Calling the Amadeus `shopping.flight_offers_search.get()` endpoint
- Filtering results to prioritize American Airlines (`AA`) carrier code where available
- Extracting flight number, departure time, arrival time, and price per person
- Returning a list of the top results formatted and ready to write to the sheet

---

### `hotels.py`
Scrapes hotel listings for both the Disney World area and Universal Orlando area, then splits them into two result sets matching the two-phase trip plan. Responsible for:

- Accepting check-in date, check-out date, number of Phase 1 nights, number of Phase 2 nights, and number of guests
- Scraping a travel aggregator (e.g. Booking.com via Serpapi, or direct hotel sites) for hotels near Walt Disney World and near Universal Orlando separately
- For each hotel, extracting and returning:
  - **Hotel name**
  - **Star rating** (1–5 stars)
  - **Price per night**
  - **Total cost** for the relevant phase (price × nights)
  - **Distance from each relevant park gate** in miles — or a special location tag if the hotel is on Disney/Universal property (see below)
  - **On-site perks** such as: Early Park Entry eligibility, Disney transport / Skyliner access, Lightning Lane discounts, Express Pass inclusion, on-site water taxi, free parking, etc.

**Location tag logic:**
- If a hotel is an official Disney resort physically inside or immediately adjacent to a park (e.g. Disney's Beach Club Resort beside EPCOT's International Gateway), `hotels.py` will tag it as `Inside EPCOT` rather than showing a distance
- Other Disney-owned resorts get tagged as `Disney Resort — [area]` (e.g. `Disney Resort — Magic Kingdom Area`)
- Universal on-site hotels (Premier, Preferred, or Standard tier) get tagged as `On-site Universal — [tier]` since Premier hotels include complimentary Express Pass
- Off-property hotels show distance in miles to the nearest park entrance

**Why this matters for your trip plan:**
- Phase 1 (Disney stay) should prioritise EPCOT-area resorts for easy International Gateway access and the EPCOT Skyliner connection to Hollywood Studios
- Phase 2 (Universal stay) should highlight Premier-tier on-site hotels since they include Express Pass, which is otherwise a significant added cost

> **Scraping note:** Websites change their HTML structure over time. If scraping breaks, the selectors (CSS classes or tag names used to find data) in this file may need to be updated. This is a normal maintenance task for any scraping-based project.

---

### `parks.py`
Scrapes admission prices for Walt Disney World and Universal Orlando and pairs them with ride and fast-pass data from the `data/` reference files. Responsible for:

- Scraping Disney World ticket pricing from `disneyworld.disney.go.com`
- Scraping Universal Orlando ticket pricing from `universalorlando.com`
- Extracting ticket types (1-Day Base, Multi-Day, Park Hopper, Park Hopper Plus) and per-person prices
- Calculating total cost based on number of travelers
- Loading the ride lists from `data/disney_rides.py` and `data/universal_rides.py`
- For each park, attaching:
  - **Full ride list** with ride name, thrill level (Mild / Moderate / Thrill), and any height requirements
  - **Lightning Lane status** for Disney rides: not eligible / Lightning Lane Multi Pass / Lightning Lane Single Pass (premium)
  - **Express Pass status** for Universal rides: included with Premier hotel / purchasable add-on / not eligible
  - **Notes** on fan favourites, typically long wait times, or seasonal availability
- Returning everything formatted and ready to write to the Parks tabs in the sheet

**Disney parks covered:**
- Magic Kingdom
- EPCOT
- Hollywood Studios
- Animal Kingdom

**Universal parks covered:**
- Universal Studios Florida
- Islands of Adventure
- Epic Universe *(opened May 2025 — ride list will be in `data/universal_rides.py`)*

> **Static fallback:** Because park pricing pages can be complex and JavaScript-rendered, `parks.py` will include a hardcoded fallback price table that you can manually update from the official sites if scraping fails. This makes the module resilient.

> **Ride data note:** Ride lists in the `data/` folder are maintained manually. Disney and Universal do not publish structured ride data via any API. The lists will be seeded with all current attractions at the time the project is built. Update them when new rides open or close.

---

### `booking_windows.py`
Calculates the earliest date you can book each component of your trip and writes those dates back to the sheet. Responsible for:

- Accepting your trip arrival date as input
- Holding a hardcoded dictionary of booking window rules for every bookable item (flights, hotels, park tickets, Lightning Lane, Express Pass, dining)
- For each item, calculating the earliest booking date by subtracting the window in days from your arrival date
- Comparing the earliest booking date against today's date to produce a status and countdown
- Returning a structured list ready to write to both the `Inputs` tab summary rows and the full `Booking Windows` tab

**The booking rules dictionary in this file looks like:**

```python
BOOKING_WINDOWS = {
    "American Airlines flights": {
        "days_before": 331,
        "anchor": "departure_date",   # calculate from departure, not arrival
        "notes": "AA opens exactly 331 days before departure. Set a calendar reminder.",
        "url": "https://www.aa.com",
    },
    "Disney Resort hotels": {
        "days_before": 499,
        "anchor": "check_in_date",
        "notes": "General public window. Disney Vacation Club members may access earlier.",
        "url": "https://disneyworld.disney.go.com/reservations/hotels/",
    },
    "Disney park tickets": {
        "days_before": None,          # No hard window — available any time
        "anchor": None,
        "notes": "No advance window, but prices increase closer to date. Buy early.",
        "url": "https://disneyworld.disney.go.com/admission/tickets/",
    },
    "Disney Lightning Lane Multi Pass": {
        "days_before": 0,             # Day-of only
        "anchor": "park_date",
        "notes": "Purchased day-of at 7:00am. On-site guests can book from resort.",
        "url": "https://disneyworld.disney.go.com/experience-updates/lightning-lane/",
    },
    "Disney dining reservations": {
        "days_before": 60,
        "anchor": "dining_date",
        "notes": "Most popular restaurants book within hours. Set an alarm for 6:00am on opening day.",
        "url": "https://disneyworld.disney.go.com/dining/",
    },
    # ... and so on for all items
}
```

- `days_before` is how many days before the anchor date the booking window opens
- `anchor` tells the module which date to calculate from (arrival, departure, or a specific park/dining date)
- Items with `days_before: 0` are day-of only and are flagged accordingly
- Items with `days_before: None` have no hard window and show `Available any time`

**Status labels written to the sheet:**

| Condition | Status Label |
|---|---|
| Earliest date is in the future | `Opens in X days (YYYY-MM-DD)` |
| Earliest date is today | `OPENS TODAY` |
| Earliest date has passed | `OPEN — book now` |
| No hard window | `Available any time` |
| Day-of only | `Day-of purchase only` |

> **Keeping rules up to date:** Disney and Universal occasionally change booking policies. The `BOOKING_WINDOWS` dictionary in this file is your single source of truth — update the `days_before` value for any item that changes and re-run the script to refresh all dates in the sheet.

---

### `trip_strategy.py`
Handles the two-phase trip logic and all park-days-to-hotel-nights conversion. Responsible for:

- Reading Disney days and Universal days from the Inputs tab if provided
- Converting park days to hotel nights using the transition day formula:
  - Disney hotel nights = Disney days − 1
  - Universal hotel nights = Universal days − 1
  - Switch day is Universal night 1 (no double-counting)
- Writing the calculated phase nights back to the Phase 1 and Phase 2 rows in the Inputs tab so you can see and verify the conversion
- If park days are not given, reading the manually entered phase nights directly instead
- Validating that the derived total hotel nights matches the trip length when specific dates are present — warning (not stopping) if they differ
- Splitting hotel results into the Disney phase and Universal phase
- Calculating per-phase subtotals (hotels + parks for each phase)
- Flagging hotels with significant perks relevant to the strategy:
  - EPCOT-area Disney resorts with Skyliner access
  - Universal Premier hotels where the included Express Pass may offset the higher room rate
- Passing all phase data to `sheets.py` for writing to the correct tabs

---

### `data/disney_rides.py`
A Python dictionary of all Walt Disney World attractions organised by park. Each ride entry contains:

```python
{
  "name": "Guardians of the Galaxy: Cosmic Rewind",
  "park": "EPCOT",
  "thrill_level": "Thrill",
  "height_req": "42 inches",
  "lightning_lane": "Single Pass",  # or "Multi Pass" or "None"
  "notes": "Virtual queue or ILL required — books up fast"
}
```

Update this file manually when new attractions open or close.

---

### `data/universal_rides.py`
Same structure as `disney_rides.py` but for Universal Orlando's three parks. Express Pass field values:
- `"Included"` — complimentary with Premier on-site hotel
- `"Add-on"` — purchasable separately
- `"None"` — not eligible for Express Pass

---
Prints a clean, readable cost summary to the terminal using the `rich` library. Responsible for:
- Accepting the compiled results from all three modules
- Displaying a formatted table in the terminal showing all costs
- Showing the per-person breakdown and grand total
- Confirming the sheet has been updated successfully

---

### `main.py`
The entry point. Reads the mode dropdown and orchestrates the right pipeline. Responsible for:

- Loading environment variables
- Connecting to the Google Sheet via `sheets.py`
- Reading the mode dropdown value from B3 on the Inputs sheet
- Reading all input cells and applying conditional formatting rules so greyed fields are ignored even if they contain a value
- Validating inputs relevant to the selected mode — writing the status to the Inputs sheet immediately before any API calls run
- Hiding unused columns and rows on the Inputs sheet after validation so the sheet stays contained
- Running only the pipeline for the selected mode and writing results only to that mode's output sheet
- Leaving the other two output sheets completely untouched
- Calling `report.py` to print the terminal summary

---

## 11. Running the Project

Once all modules are built and configured:

### Standard Run

1. Open your Google Sheet and fill in your inputs on the `Inputs` tab
2. Open a terminal and navigate to your project folder:
   ```bash
   cd path/to/disney_trip_planner
   ```
3. Run the script:
   ```bash
   python main.py
   ```
4. Watch the terminal output as each module runs
5. Open your Google Sheet — the relevant tabs will be populated

### What You Should See in the Terminal

**Mode 1 — Explore (no dates):**
```
Disney Trip Planner Starting...
──────────────────────────────────────
Connected to Google Sheet
Inputs read:
   Origin:   JFK
   Dates:    None provided
   People:   1 (default)

Mode detected: EXPLORE — generating 24-month price overview
   Coverage: Jun 2026 → May 2028

Fetching price data...
   [██████████████████░░] 22/24 months...  Done
   Amadeus API calls used: 56

Writing to 1 - Explore sheet...  Done
──────────────────────────────────────
PRICE OVERVIEW — cheapest months for JFK → MCO
──────────────────────────────────────
  Sep 2026   Value     ~$1,820 total/person
  Jan 2027   Value     ~$1,750 total/person
  Sep 2027   Value     ~$1,810 total/person
  Dec 2026   Peak      ~$3,400 total/person  (peak) Christmas premium
──────────────────────────────────────
Google Sheet updated — see 1 - Explore sheet.
```

**Mode 2 — Month View:**
```
Disney Trip Planner Starting...
──────────────────────────────────────
Connected to Google Sheet
Inputs read:
   Origin:      JFK
   Month/Year:  2026-12
   People:      2

Mode detected: MONTH VIEW — week-by-week breakdown for Dec 2026

Calculating booking windows (anchor: 2026-12-01)...  Done
Fetching weekly flight + hotel prices...  Done
Fetching park prices...  Done

Writing to 2 - Month View sheet...  Done
──────────────────────────────────────
DECEMBER 2026 OVERVIEW  (2 travelers)
──────────────────────────────────────
  Week 1  Dec 1–7     Flights ~$620pp  Hotels ~$180/nt  Moderate
  Week 2  Dec 8–14    Flights ~$640pp  Hotels ~$190/nt  Moderate
  Week 3  Dec 15–21   Flights ~$780pp  Hotels ~$240/nt  (rising)
  Week 4  Dec 22–31   Flights ~$980pp  Hotels ~$380/nt  (peak)
──────────────────────────────────────
Google Sheet updated — see 2 - Month View sheet.
```

**Mode 3 — Full Plan:**
```
Disney Trip Planner Starting...
──────────────────────────────────────
Connected to Google Sheet
Inputs read:
   Origin:   JFK
   Arrive:   2026-12-01
   Depart:   2026-12-14
   People:   4
   Phase 1:  9 nights (Disney)
   Phase 2:  4 nights (Universal)

Mode detected: FULL PLAN

Calculating booking windows...  Done
Searching flights...  Done (5 results)
Searching hotels...   Done (8 results)
Fetching park prices... Done (7 results)
Writing results to 3 - Full Plan sheet...  Done

──────────────────────────────────────
TRIP SUMMARY
──────────────────────────────────────
Flights Total:   $3,200.00
Hotels Total:    $4,150.00  (Phase 1: $2,700 | Phase 2: $1,450)
Parks Total:     $2,400.00
──────────────────────────────────────
GRAND TOTAL:     $9,750.00  ($2,437.50 per person)
──────────────────────────────────────
Google Sheet updated successfully.
```

---

## 12. Adding a Watch Loop

If you want the script to run automatically when you change a cell (instead of manually running it each time), you can add a polling loop to `main.py`.

The concept is:

1. When the script starts, it reads the current input values and stores them
2. Every 30 seconds, it reads the inputs again
3. If anything has changed, it runs the full pipeline and updates the sheet
4. If nothing has changed, it waits and checks again

This turns the script into a background process that auto-updates the sheet whenever you edit the inputs. You would start it once in the morning and leave it running in the background:

```bash
python main.py --watch
```

> **API call awareness:** With the watch loop, be mindful of the Amadeus free tier limit of 2,000 calls/month. The loop should only trigger when inputs actually change, not on every poll interval.

---

## 13. Deployment on PythonAnywhere (Optional)

If you want the script to run in the cloud so you do not need to keep your computer on, PythonAnywhere's free tier works well for this.

### Steps

1. Create a free account at https://www.pythonanywhere.com
2. Go to the **Files** tab and upload your project folder
3. Upload your `credentials.json` and `.env` file too
4. Open a **Bash console** and install dependencies:
   ```bash
   pip3 install --user gspread google-auth requests beautifulsoup4 python-dotenv rich amadeus
   ```
5. Test that it runs:
   ```bash
   python3 main.py
   ```
6. Go to the **Tasks** tab to set up a scheduled run (e.g. every hour, or daily)

> **Free tier limits on PythonAnywhere:** Scheduled tasks on the free plan run at most once daily. For on-demand runs, you can manually trigger from the console. Upgrading to a paid plan ($5/month) allows more frequent scheduling, but the free tier is sufficient for planned trip research.

---

## 14. Troubleshooting

### `gspread.exceptions.SpreadsheetNotFound`
- Make sure you shared the sheet with the service account's `client_email`
- Double-check the `GOOGLE_SHEET_ID` in your `.env` matches the URL of your sheet

### `google.auth.exceptions.TransportError`
- Check your internet connection
- Confirm `credentials.json` is in the project folder and the path in `.env` is correct

### Amadeus `AuthenticationError`
- Verify `AMADEUS_API_KEY` and `AMADEUS_API_SECRET` in `.env` match exactly what is in your Amadeus dashboard
- Make sure there are no extra spaces or quotes around the values

### `No flights found` (Mode 3)
- The Amadeus test environment has limited routes. Try a major airport like `JFK`, `LAX`, `ORD`, or `ATL`
- Confirm your dates are in `YYYY-MM-DD` format
- Make sure the arrival date is before the departure date

### `Month/Year conflict error`
- If you have both Month/Year (B3) and specific arrival date (B4) filled in, they must be the same calendar month
- Either clear the Month/Year cell or update your arrival date to match

### `Travelers defaulted to 1 unexpectedly`
- If B6 is blank the script defaults to 1 traveler and notes this in the terminal
- Fill in B6 with your actual number if this is not what you intended

### `Price Explorer shows — for some months`
- Amadeus test environment data is sparse for dates far in the future (18–24 months out)
- The script writes `No data` for months where no results were returned rather than showing a wrong number
- This is an Amadeus test environment limitation — data coverage improves for dates within the next 12 months

### `No airport given — script exits immediately`

### Scraping returns empty results (hotels or parks)
- The website may have changed its HTML structure
- Open the target URL in your browser, right-click the price element, and click **Inspect** to find the new CSS class or tag to target in your scraper
- As a fallback, use the hardcoded price table in `parks.py`

### `.env` values not loading
- Confirm the `.env` file is in the same folder as `main.py`
- Make sure `load_dotenv()` is called at the top of `main.py` before anything else reads the environment

---

## 15. Limitations & Notes

| Area | Limitation | Notes |
|---|---|---|
| **Flights** | Amadeus test environment uses simulated data | Prices are realistic estimates but not live fares. Sufficient for planning. |
| **Flights** | 2,000 API calls/month on free tier | Each run uses ~1 call. Running daily for a month = 30 calls. Well within limits. |
| **Hotels** | No official free Disney or Universal hotel API | Relies on web scraping a travel aggregator. On-site perks (Early Entry, Express Pass) are tagged from the hardcoded hotel knowledge in `hotels.py` rather than scraped, since they are consistent and rarely change |
| **Hotels** | Distance calculations are approximate | Distances to park gates are estimated from known coordinates, not live mapping data |
| **Rides** | No public ride API exists | Ride lists and fast-pass eligibility are maintained manually in `data/disney_rides.py` and `data/universal_rides.py` |
| **Epic Universe** | Opened May 2025 — new park | Ride list and pricing will need to be populated manually in the data files at project build time |
| **Parks** | Disney/Universal ticket pages use JavaScript rendering | Static scraping may not always work. Hardcoded fallback prices are included as a backup. |
| **Mode 1 price estimates** | Prices are sampled averages, not guaranteed fares | 2–3 sample dates per month are queried and averaged. Use for relative comparison between months, not precise budgeting. Mode 3 gives accurate numbers for specific dates. |
| **Mode 1 far-future months** | Amadeus test data is sparse beyond 12 months | Months 13–24 may show `No data` for flights. The hotel and park columns will still populate from seasonal estimates. |
| **Mode 2 week breakdown** | Hotel weekly variation is estimated, not scraped live | Week-by-week hotel price shifts are based on known seasonal patterns rather than live scraping of all weeks. |
| **Park days vs trip length** | Mismatch is a warning not an error | If park days imply a different total than your specific dates, the script warns you but runs Mode 3 anyway using the specific dates as the authoritative source. You decide which to trust. |
| **Lightning Lane** | Day-of only — no advance booking | This is a Disney policy, not a project limitation. The sheet flags these clearly so there is no confusion. |
| **Currency** | All prices returned in USD | No conversion needed for a Florida trip |
| **Real-time availability** | Hotel availability is not checked | Prices shown are listed rates, not guaranteed availability |

---

## You Are Ready to Build

With this README as your guide, the build order is:

1. Complete Google Cloud Setup (Section 6)
2. Set up your Google Sheet tabs and layout (Section 7)
3. Create your Amadeus account and get keys (Section 8)
4. Fill in your `.env` file (Section 9)
5. Build `data/disney_rides.py` — seed the ride list from the Walt Disney World website
6. Build `data/universal_rides.py` — seed the ride list from the Universal Orlando website
7. Build `config.py` — sheet tab names, cell references, mode detection constants
8. Build `booking_windows.py` — no external dependencies; test standalone against a few sample dates
9. Build `sheets.py` — test reading inputs and writing to each tab; test the mode/status rows in the Inputs tab
10. Build `price_explorer.py` — start with Mode 1 (24-month grid), then add Mode 2 (weekly breakdown); test with a hardcoded airport and month before wiring to the sheet
11. Build `flights.py` — test with hardcoded inputs
12. Build `hotels.py` — test Disney area first, then Universal area
13. Build `parks.py` — test pricing scrape + ride data attachment
14. Build `trip_strategy.py` — implement the park-days-to-hotel-nights conversion formula first, then phase split logic and perk flagging; test the conversion with several day combinations including edge cases (e.g. only Disney days given, days that don't match trip length)
15. Build `report.py`
16. Build `main.py` — wire everything together; implement mode detection and input validation first before connecting any data modules
17. Test Mode 1 end to end (airport only)
18. Test Mode 2 end to end (airport + month/year)
19. Test Mode 3 end to end (airport + full dates)
20. Test Mode 3 with park days filled in — verify phase nights auto-fill correctly
21. Test conflict detection (mismatched month/year and dates, park days vs trip length mismatch)

---

## Two-Phase Trip Strategy — Context for the Code

Understanding your trip plan helps make sense of some design decisions in the code:

**Phase 1 — Disney Stay (longer)**
The goal is to be based inside or right next to EPCOT. Disney's EPCOT-area resorts (Beach Club, Yacht Club, BoardWalk, Caribbean Beach) sit within walking distance of EPCOT's International Gateway entrance and connect via the Disney Skyliner gondola to Hollywood Studios and Art of Animation. This means no car or bus needed for two of the four parks. `hotels.py` will flag these resorts specifically and tag them `Inside EPCOT` or `EPCOT Area — Skyliner Access`.

All Disney on-site guests also receive **Early Theme Park Entry** (30 minutes before public opening) every day, which is a meaningful perk for beating crowds on popular rides. This perk is tagged in the hotel output.

**Phase 2 — Universal Stay (shorter)**
The goal is convenience for Universal's parks. Universal's on-site Premier hotels (Portofino Bay, Hard Rock Hotel, Royal Pacific Resort) include **complimentary Universal Express Pass** for all registered guests for all nights of the stay. Express Pass lets you skip the standby queue on most rides — a $100+ per person per day value. `hotels.py` will calculate whether the higher room rate of a Premier hotel is offset by the Express Pass value, and flag it clearly. Epic Universe (the newest park) is walking distance from several off-site hotels on International Drive as well.

When you are ready to start writing code for any module, refer back to the **Module Breakdown** in Section 10 for a clear description of what each file needs to do.

---

## Future Extension — Generalising Beyond Florida and Disney

This section is not part of the current build. It documents how the planner could be extended to cover any fly-to trip once the Florida version is complete and stable. The architecture already supports most of this with relatively minor changes — nothing here requires a structural rebuild.

**What to change and where:**

`config.py` and the Inputs sheet — Add a destination airport field and an optional destination city or landmark field alongside the existing origin airport. MCO and Orlando are currently hardcoded in config; replacing them with user inputs is a one-line change in config and one additional row on the Inputs sheet. The Amadeus flight search in `flights.py` already accepts any IATA pair and requires no changes at all.

`hotels.py` — Distance calculations currently use Disney and Universal park gates as fixed reference points. Replacing these with the user-supplied destination landmark or city centre makes the proximity logic work for any destination. The rest of the module — scraping, star ratings, nightly price, on-site perks — is already generic.

`parks.py` and the `data/` folder — This is the most Disney-specific part of the project. For a generic trip the park section becomes an optional activities section. If the user leaves it blank the script skips it. If they fill it in they can enter any attraction, admission price, and notes — the data shape is the same whether it is a theme park, a museum, a sporting event, or a day tour. The `data/disney_rides.py` and `data/universal_rides.py` files have no equivalent for a generic trip and simply would not be used.

`booking_windows.py` — The Disney and Universal specific windows (Lightning Lane, Express Pass, dining reservations) would be omitted for non-Disney destinations. The generic rules — flights at 331 days, hotels at around 12 months — apply to any trip and stay useful without modification.

`trip_strategy.py` — The two-phase structure is already destination-agnostic in its logic. Phase 1 and Phase 2 are just two hotel stays at different bases. Renaming the labels from Disney and Universal to whatever the two locations are is the only change needed. The night conversion formula and the perk-flagging logic either apply or are simply skipped.

**What to add:**

A destination input field on the Inputs sheet is the only new field required. Everything else is a matter of making the Disney-specific sections conditional — they run if the destination is Orlando and theme park data is relevant, and are skipped otherwise.

**Recommended approach:**

Complete and thoroughly test the Florida build first. Then create a copy of the project as the starting point for the generic version. The Florida version stays intact as its own fully functional tool, and the generic version is built by progressively removing hardcoded assumptions rather than by changing anything structural.

---

*Built with Python | Powered by Amadeus, Google Sheets API, and web scraping*
