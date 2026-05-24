from datetime import date
from src.config import SEASONS

# Seasonal price multipliers
_MULTIPLIERS = {
    "Value":    0.75,
    "Moderate": 1.00,
    "Peak":     1.30,
}


def _multiplier(arrival: str | None) -> float:
    if not arrival:
        return 1.0
    month = int(arrival[5:7])
    for label, months in SEASONS.items():
        if month in months:
            return _MULTIPLIERS[label]
    return 1.0


def _total(price_per_night: float, nights: int, mult: float) -> float:
    return round(price_per_night * mult * nights, 2)


# ── Disney on-site hotels ─────────────────────────────────────────────────────
# Prices are base nightly rates (moderate season). Updated manually as needed.
# Source: disneyworld.disney.go.com/resorts

DISNEY_HOTELS = [
    # EPCOT area — recommended for Phase 1 (Skyliner + walking access)
    {
        "name": "Disney's Beach Club Resort",
        "location_tag": "Inside EPCOT (International Gateway)",
        "stars": 4,
        "base_price": 695,
        "dist_mk": "4.2 mi",
        "dist_epcot": "Walking (0.1 mi)",
        "dist_hs": "Skyliner / 0.5 mi",
        "dist_ak": "5.1 mi",
        "perks": "Early Park Entry · Walking distance to EPCOT International Gateway · Stormalong Bay pool · Skyliner to Hollywood Studios",
        "epcot_area": True,
    },
    {
        "name": "Disney's Yacht Club Resort",
        "location_tag": "Inside EPCOT (International Gateway)",
        "stars": 4,
        "base_price": 675,
        "dist_mk": "4.2 mi",
        "dist_epcot": "Walking (0.1 mi)",
        "dist_hs": "Skyliner / 0.5 mi",
        "dist_ak": "5.1 mi",
        "perks": "Early Park Entry · Walking distance to EPCOT International Gateway · Stormalong Bay pool",
        "epcot_area": True,
    },
    {
        "name": "Disney's BoardWalk Inn",
        "location_tag": "Inside EPCOT (International Gateway)",
        "stars": 4,
        "base_price": 555,
        "dist_mk": "4.2 mi",
        "dist_epcot": "Walking (0.2 mi)",
        "dist_hs": "Skyliner / 0.4 mi",
        "dist_ak": "5.1 mi",
        "perks": "Early Park Entry · Walking distance to EPCOT International Gateway · Skyliner to Hollywood Studios",
        "epcot_area": True,
    },
    {
        "name": "Disney's Caribbean Beach Resort",
        "location_tag": "EPCOT Area — Skyliner Hub",
        "stars": 3,
        "base_price": 315,
        "dist_mk": "4.5 mi",
        "dist_epcot": "Skyliner (10 min)",
        "dist_hs": "Skyliner (8 min)",
        "dist_ak": "5.0 mi",
        "perks": "Early Park Entry · Skyliner hub (connects to EPCOT & Hollywood Studios)",
        "epcot_area": True,
    },
    {
        "name": "Disney's Art of Animation Resort",
        "location_tag": "EPCOT Area — Skyliner Access",
        "stars": 3,
        "base_price": 245,
        "dist_mk": "5.0 mi",
        "dist_epcot": "Skyliner (12 min)",
        "dist_hs": "Skyliner (10 min)",
        "dist_ak": "5.8 mi",
        "perks": "Early Park Entry · Skyliner to EPCOT & Hollywood Studios · Family suite rooms available",
        "epcot_area": True,
    },
    {
        "name": "Disney's Pop Century Resort",
        "location_tag": "EPCOT Area — Skyliner Access",
        "stars": 2,
        "base_price": 215,
        "dist_mk": "5.0 mi",
        "dist_epcot": "Skyliner (12 min)",
        "dist_hs": "Skyliner (10 min)",
        "dist_ak": "5.8 mi",
        "perks": "Early Park Entry · Skyliner to EPCOT & Hollywood Studios · Best-value on-site option",
        "epcot_area": True,
    },
    # Magic Kingdom area
    {
        "name": "Disney's Grand Floridian Resort & Spa",
        "location_tag": "Disney Resort — Magic Kingdom Area",
        "stars": 5,
        "base_price": 895,
        "dist_mk": "Walking (0.3 mi) / Monorail",
        "dist_epcot": "3.9 mi",
        "dist_hs": "4.5 mi",
        "dist_ak": "6.0 mi",
        "perks": "Early Park Entry · Monorail to Magic Kingdom · Signature dining · Spa",
        "epcot_area": False,
    },
    {
        "name": "Disney's Polynesian Village Resort",
        "location_tag": "Disney Resort — Magic Kingdom Area",
        "stars": 4,
        "base_price": 745,
        "dist_mk": "Monorail / 0.5 mi",
        "dist_epcot": "3.9 mi",
        "dist_hs": "4.5 mi",
        "dist_ak": "6.0 mi",
        "perks": "Early Park Entry · Monorail to Magic Kingdom · Beach views · Bora Bora bungalows",
        "epcot_area": False,
    },
    {
        "name": "Disney's Contemporary Resort",
        "location_tag": "Disney Resort — Magic Kingdom Area",
        "stars": 4,
        "base_price": 645,
        "dist_mk": "Walking (0.3 mi) / Monorail",
        "dist_epcot": "4.0 mi",
        "dist_hs": "4.6 mi",
        "dist_ak": "6.1 mi",
        "perks": "Early Park Entry · Monorail through the building · Walking distance to Magic Kingdom",
        "epcot_area": False,
    },
    {
        "name": "Disney's Wilderness Lodge",
        "location_tag": "Disney Resort — Magic Kingdom Area",
        "stars": 4,
        "base_price": 445,
        "dist_mk": "Boat (15 min)",
        "dist_epcot": "4.5 mi",
        "dist_hs": "5.0 mi",
        "dist_ak": "6.5 mi",
        "perks": "Early Park Entry · Boat to Magic Kingdom · Pacific Northwest theming · Roaring Fork quick service",
        "epcot_area": False,
    },
    # Animal Kingdom area
    {
        "name": "Disney's Animal Kingdom Lodge",
        "location_tag": "Disney Resort — Animal Kingdom Area",
        "stars": 4,
        "base_price": 475,
        "dist_mk": "6.2 mi",
        "dist_epcot": "5.5 mi",
        "dist_hs": "5.0 mi",
        "dist_ak": "0.5 mi",
        "perks": "Early Park Entry · Savanna views with live animals · Jiko and Boma signature dining",
        "epcot_area": False,
    },
    # Value
    {
        "name": "Disney's All-Star Movies Resort",
        "location_tag": "Disney Resort — Animal Kingdom Area",
        "stars": 2,
        "base_price": 175,
        "dist_mk": "6.5 mi",
        "dist_epcot": "5.8 mi",
        "dist_hs": "5.2 mi",
        "dist_ak": "1.2 mi",
        "perks": "Early Park Entry · Bus transport to all parks · Most affordable on-site option",
        "epcot_area": False,
    },
]

# ── Universal on-site hotels ──────────────────────────────────────────────────
# Source: universalorlando.com/hotels

UNIVERSAL_HOTELS = [
    # Premier — includes complimentary Express Pass for all guests all nights
    {
        "name": "Loews Portofino Bay Hotel",
        "location_tag": "On-site Universal — Premier",
        "stars": 4,
        "base_price": 375,
        "tier": "Premier",
        "dist_usf": "Water taxi / 0.4 mi",
        "dist_ioa": "Water taxi / 0.5 mi",
        "dist_epic": "1.8 mi",
        "perks": "Complimentary Express Pass (all nights) · Early Park Admission · Water taxi to CityWalk · Portofino-inspired resort",
        "express_included": True,
    },
    {
        "name": "Hard Rock Hotel",
        "location_tag": "On-site Universal — Premier",
        "stars": 4,
        "base_price": 340,
        "tier": "Premier",
        "dist_usf": "Walking (0.2 mi)",
        "dist_ioa": "Walking (0.2 mi)",
        "dist_epic": "1.6 mi",
        "perks": "Complimentary Express Pass (all nights) · Early Park Admission · Walking distance to both parks · Rock music theming",
        "express_included": True,
    },
    {
        "name": "Loews Royal Pacific Resort",
        "location_tag": "On-site Universal — Premier",
        "stars": 4,
        "base_price": 295,
        "tier": "Premier",
        "dist_usf": "Water taxi / 0.4 mi",
        "dist_ioa": "Water taxi / 0.4 mi",
        "dist_epic": "1.7 mi",
        "perks": "Complimentary Express Pass (all nights) · Early Park Admission · Water taxi to CityWalk · Best-value Premier hotel",
        "express_included": True,
    },
    # Preferred — no Express Pass included
    {
        "name": "Loews Sapphire Falls Resort",
        "location_tag": "On-site Universal — Preferred",
        "stars": 3,
        "base_price": 235,
        "tier": "Preferred",
        "dist_usf": "Water taxi / 0.5 mi",
        "dist_ioa": "Water taxi / 0.5 mi",
        "dist_epic": "1.5 mi",
        "perks": "Early Park Admission · Water taxi to CityWalk · Caribbean theming · No Express Pass included",
        "express_included": False,
    },
    # Standard
    {
        "name": "Universal's Cabana Bay Beach Resort",
        "location_tag": "On-site Universal — Standard",
        "stars": 3,
        "base_price": 175,
        "tier": "Standard",
        "dist_usf": "Shuttle / 0.6 mi",
        "dist_ioa": "Shuttle / 0.6 mi",
        "dist_epic": "0.4 mi",
        "perks": "Early Park Admission · Shuttle to CityWalk · Closest hotel to Epic Universe · On-site water park · Retro 1960s theming",
        "express_included": False,
    },
    {
        "name": "Universal's Aventura Hotel",
        "location_tag": "On-site Universal — Standard",
        "stars": 3,
        "base_price": 195,
        "tier": "Standard",
        "dist_usf": "Shuttle / 0.5 mi",
        "dist_ioa": "Shuttle / 0.5 mi",
        "dist_epic": "0.3 mi",
        "perks": "Early Park Admission · Shuttle to CityWalk · Modern tower hotel · Close to Epic Universe",
        "express_included": False,
    },
    {
        "name": "Universal's Endless Summer Resort — Surfside Inn",
        "location_tag": "On-site Universal — Standard",
        "stars": 2,
        "base_price": 135,
        "tier": "Standard",
        "dist_usf": "Shuttle / 1.2 mi",
        "dist_ioa": "Shuttle / 1.2 mi",
        "dist_epic": "0.8 mi",
        "perks": "Early Park Admission · Shuttle to parks · Most affordable on-site Universal option",
        "express_included": False,
    },
]


def get_disney_hotels(nights: int, arrival: str | None = None) -> list[dict]:
    mult = _multiplier(arrival)
    result = []
    for h in DISNEY_HOTELS:
        entry = dict(h)
        entry["price_per_night"] = round(h["base_price"] * mult, 2)
        entry["phase_total"] = _total(h["base_price"], nights, mult)
        result.append(entry)
    return result


def get_universal_hotels(nights: int, arrival: str | None = None) -> list[dict]:
    mult = _multiplier(arrival)
    result = []
    for h in UNIVERSAL_HOTELS:
        entry = dict(h)
        entry["price_per_night"] = round(h["base_price"] * mult, 2)
        entry["phase_total"] = _total(h["base_price"], nights, mult)
        result.append(entry)
    return result
