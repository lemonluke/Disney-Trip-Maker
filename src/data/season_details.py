"""
Per-month season details for the Disney Florida trip planner.
Each entry covers weather, EPCOT festivals, after-hours events,
crowd spikes, best weeks, and a practical planning tip.
"""

SEASON_DETAILS = {
    1: {
        "season":         "Value",
        "weather":        "55–72°F · Cool, low humidity · Jacket needed evenings · Some rain",
        "epcot_festival": "Festival of the Arts (mid-Jan – mid-Feb)",
        "after_hours":    None,
        "crowd_spikes":   "MLK weekend (3rd Mon) — moderate spike",
        "park_hours":     "Short — parks close 9–10pm most nights",
        "refurbs":        "Peak refurb season — several rides closed for maintenance",
        "best_weeks":     "Jan 2–14 (quietest stretch of the entire year)",
        "tip": (
            "Jan 2–14 is the single best value window of the year — extremely low crowds, "
            "short waits, and no need for Lightning Lane Multi Pass on most rides. "
            "Festival of the Arts makes EPCOT especially worth visiting. "
            "Avoid MLK weekend. Expect some rides to be closed for refurbishment."
        ),
    },
    2: {
        "season":         "Value",
        "weather":        "60–76°F · Warming late Feb · Low humidity · Pleasant and dry",
        "epcot_festival": "Festival of the Arts (through mid-Feb) → Flower & Garden begins late Feb",
        "after_hours":    None,
        "crowd_spikes":   "Presidents' Day weekend (3rd Mon) — moderate spike",
        "park_hours":     "Short — parks close 9–10pm most nights",
        "refurbs":        "Refurb season continues — check ride closures before booking",
        "best_weeks":     "Feb 1–14 (before Presidents' Day crowds build)",
        "tip": (
            "Early February is very quiet and the weather starts to feel genuinely pleasant. "
            "Flower and Garden begins late Feb — a good reason to prioritise EPCOT. "
            "Avoid Presidents' Day weekend. Lightning Lane Multi Pass rarely needed "
            "outside of the top Single Pass rides."
        ),
    },
    3: {
        "season":         "Moderate",
        "weather":        "65–82°F · Warm, pleasant · Afternoon showers begin · Humidity rising",
        "epcot_festival": "Flower & Garden Festival (late Feb – late May)",
        "after_hours":    None,
        "crowd_spikes":   "Spring Break (typically runs 2–3 weeks mid-March through early April) — very busy",
        "park_hours":     "Extended around Spring Break — parks open until 11pm–midnight",
        "refurbs":        "Most refurbs complete by early March",
        "best_weeks":     "March 1–7 (before Spring Break begins)",
        "tip": (
            "The first week of March can be excellent — warm, Flower & Garden running, "
            "crowds still low before Spring Break hits. "
            "Mid-March through early April is one of the busiest periods of the year. "
            "If your travel dates overlap Spring Break, treat it like a Peak month — "
            "Lightning Lane Multi Pass is worth buying and rope-drop strategy is essential."
        ),
    },
    4: {
        "season":         "Moderate",
        "weather":        "70–86°F · Warm and humid · Daily afternoon thunderstorms begin",
        "epcot_festival": "Flower & Garden Festival (through late May)",
        "after_hours":    None,
        "crowd_spikes":   "Easter weekend — major spike (date varies, can fall in Mar or Apr)",
        "park_hours":     "Extended around Easter — parks open late",
        "refurbs":        "Minimal",
        "best_weeks":     "Late April after Easter and Spring Break clear out",
        "tip": (
            "Late April (after Easter) is underrated — warm weather, Flower & Garden in "
            "full bloom at EPCOT, and crowds noticeably lower than March. "
            "Check the Easter date for your year — if it falls in April, "
            "avoid that week. Otherwise late April is a solid moderate-month choice."
        ),
    },
    5: {
        "season":         "Moderate",
        "weather":        "76–90°F · Warm and humid · Daily afternoon thunderstorms · Summer heat building",
        "epcot_festival": "Flower & Garden Festival (through late May)",
        "after_hours":    None,
        "crowd_spikes":   "Memorial Day weekend (last Mon) — significant spike",
        "park_hours":     "Moderate to extended",
        "refurbs":        "Minimal",
        "best_weeks":     "May 1–24 (before Memorial Day weekend)",
        "tip": (
            "Early May before Memorial Day is one of the most underrated times to visit. "
            "Schools are still in session across most of the US, crowds are noticeably "
            "lower than summer, and Flower & Garden is still running at EPCOT. "
            "Avoid Memorial Day weekend. Start planning for the afternoon heat and storms."
        ),
    },
    6: {
        "season":         "Peak",
        "weather":        "88–95°F · Very hot and humid · Feels like 100°F+ · Daily storms 3–5pm",
        "epcot_festival": "None (gap between Flower & Garden ending and Food & Wine starting)",
        "after_hours":    None,
        "crowd_spikes":   "Entire month — school is out nationwide",
        "park_hours":     "Extended — parks often open until midnight",
        "refurbs":        "Minimal",
        "best_weeks":     "Early June (slightly less busy before summer fully kicks in)",
        "tip": (
            "Arrive at rope drop, hit major rides first, take a midday break noon–3pm "
            "(heat and storms peak), and return for the evening session. "
            "Lightning Lane Multi Pass is worth buying every park day in June. "
            "Ponchos are essential — afternoon storms are short but very heavy. "
            "Stay hydrated and book any indoor dining as a midday break."
        ),
    },
    7: {
        "season":         "Peak",
        "weather":        "90–96°F · Extremely hot and humid · Daily afternoon thunderstorms",
        "epcot_festival": "None",
        "after_hours":    None,
        "crowd_spikes":   "4th of July week — among the busiest days of the year · Entire month is peak",
        "park_hours":     "Extended — parks often open until midnight",
        "refurbs":        "Minimal",
        "best_weeks":     "No standout week — entire month is the busiest of the year",
        "tip": (
            "July is the single busiest month at Walt Disney World. "
            "Rope drop is non-negotiable. Buy Lightning Lane Multi Pass every day. "
            "Midday break is essential — the heat is extreme. "
            "4th of July has fireworks at Magic Kingdom but the park is packed beyond capacity. "
            "If budget allows, a Disney Deluxe resort gives Early Park Entry (30 min) "
            "which is genuinely valuable at this time of year."
        ),
    },
    8: {
        "season":         "Moderate",
        "weather":        "89–94°F · Very hot and humid · Daily storms · Slight cooling late Aug",
        "epcot_festival": "Food & Wine Festival begins mid-August (runs through mid-November)",
        "after_hours":    (
            "Mickey's Not-So-Scary Halloween Party (MNSSHP) begins select nights — "
            "Magic Kingdom closes to day guests at 6–7pm on party nights"
        ),
        "crowd_spikes":   "Early August still very busy — drops noticeably once schools resume (mid-Aug)",
        "park_hours":     "Extended early Aug · Moderate from mid-Aug",
        "refurbs":        "Minimal",
        "best_weeks":     "Mid to late August once schools are back in session",
        "tip": (
            "Mid-August is a transition point — crowds drop noticeably as US schools resume "
            "and the park feels much more manageable. EPCOT Food & Wine begins "
            "(one of the best times to visit EPCOT). "
            "Check MNSSHP dates — on party nights Magic Kingdom closes to day guests at 6–7pm. "
            "Either buy a party ticket or plan a different park on those evenings."
        ),
    },
    9: {
        "season":         "Value",
        "weather":        "87–93°F · Hot and humid · Daily afternoon storms · Hurricane season peak (Sep–Oct)",
        "epcot_festival": "Food & Wine Festival (through mid-November) — excellent addition to EPCOT days",
        "after_hours":    (
            "MNSSHP runs most Tue/Thu/Fri/Sat nights — Magic Kingdom closes to day guests 6–7pm on party nights. "
            "Halloween Horror Nights (HHN) at Universal begins select nights — worth a separate ticket."
        ),
        "crowd_spikes":   "Labor Day weekend (1st weekend) — moderate spike",
        "park_hours":     "Short — parks close 9–10pm most nights",
        "refurbs":        "Light refurbs may begin in September",
        "best_weeks":     "Mid-September weekdays (after Labor Day, quietest of the month)",
        "tip": (
            "September is widely considered the best overall month to visit Walt Disney World. "
            "Extremely low weekday crowds, short wait times, and Lightning Lane Multi Pass "
            "is rarely worth buying outside of top Single Pass rides. "
            "Food & Wine at EPCOT is in full swing. "
            "Check MNSSHP dates and either attend the party or visit a different park those evenings. "
            "Halloween Horror Nights at Universal is excellent and worth a dedicated evening."
        ),
    },
    10: {
        "season":         "Moderate",
        "weather":        "74–88°F · Cooling and drying out · Much less rain · Near-perfect by late Oct",
        "epcot_festival": "Food & Wine Festival (through mid-November)",
        "after_hours":    (
            "MNSSHP continues through early November — Magic Kingdom closes early on party nights. "
            "Halloween Horror Nights at Universal continues through early November."
        ),
        "crowd_spikes":   "Columbus Day weekend (2nd Mon) — significant spike · Halloween (Oct 31)",
        "park_hours":     "Moderate",
        "refurbs":        "Minimal",
        "best_weeks":     "Weekdays in October avoiding Columbus Day weekend",
        "tip": (
            "October is underrated. Late October weather is arguably the best of the year — "
            "cool, dry, and comfortable all day. Food & Wine still running at EPCOT. "
            "MNSSHP and HHN are both excellent seasonal events. "
            "Avoid Columbus Day weekend. Halloween day itself (Oct 31) is very busy at Magic Kingdom."
        ),
    },
    11: {
        "season":         "Moderate",
        "weather":        "63–79°F · Excellent — cool, dry, low humidity · Best weather of the year begins",
        "epcot_festival": "Food & Wine through mid-Nov → Festival of the Holidays begins late Nov",
        "after_hours":    (
            "Mickey's Very Merry Christmas Party (MVMCP) begins mid-November — "
            "Magic Kingdom closes to day guests 6–7pm on party nights. "
            "Candlelight Processional at EPCOT (special ticketed dinner packages available)."
        ),
        "crowd_spikes":   "Thanksgiving week (Wed before through Sun) — among the busiest days of the year",
        "park_hours":     "Moderate · Extended around Thanksgiving",
        "refurbs":        "Minimal",
        "best_weeks":     "November 1–20 (before Thanksgiving crowds build)",
        "tip": (
            "The first three weeks of November are a genuine hidden gem. "
            "Perfect weather, low crowds, Food & Wine at EPCOT, and MVMCP starts "
            "(either attend or avoid Magic Kingdom on party nights). "
            "Thanksgiving week is brutal — crowds rival Christmas week. "
            "If you must travel Thanksgiving, plan for Disney crowds on par with July 4th."
        ),
    },
    12: {
        "season":         "Peak",
        "weather":        "55–73°F · Cool, can be cold (low 50s some days) · Some rain · Holiday decorations everywhere",
        "epcot_festival": "Festival of the Holidays (through early January)",
        "after_hours":    (
            "MVMCP runs select nights through Dec 22 — Magic Kingdom closes early on party nights. "
            "Extra holiday overlay across all parks. EPCOT Candlelight Processional through Dec 30."
        ),
        "crowd_spikes":   "Dec 22 – Jan 1 is the single busiest period of the year · Dec 1–14 is manageable",
        "park_hours":     "Extended — parks often open until midnight in late December",
        "refurbs":        "Minimal",
        "best_weeks":     "December 1–14 (if you must go in December)",
        "tip": (
            "December 1–14 is a relative sweet spot — holiday decorations are up, "
            "Festival of the Holidays is running at EPCOT, MVMCP is on select nights, "
            "and crowds have not yet spiked. Dec 15–21 gets progressively busier. "
            "Dec 22–Jan 1 is the absolute busiest stretch of the year — "
            "plan like it's 3× July crowds. Buy Lightning Lane Multi Pass every day "
            "and arrive at rope drop."
        ),
    },
}
