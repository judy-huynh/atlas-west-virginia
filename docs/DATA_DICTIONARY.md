# WV County Master: Data Dictionary

`wv_county_master.csv`. One row per West Virginia county (55), keyed on 5-digit FIPS (`GEOID`).
Built 2026-07-13 by `build_wv_master.py`. Rebuild with `python3 build_wv_master.py`.

Area math is done in **EPSG:5070** (CONUS Albers equal-area). Source GeoJSONs are EPSG:4326.

---

## Source layers

| Layer | File | Represents | Notes |
|---|---|---|---|
| Atlas of Accountability core | `ATLAS V3 UPDATE/Master/atlas_county_master.csv` | 2011 to 2024 | Disaster declarations, FEMA PA+HM, SVI, SAIDI, older adults, race, heat |
| FEMA National Risk Index | `NRI_Counties_WV.geojson` | NRI 2023 release | 467 fields in source; a subset is carried here |
| FEMA buyouts | `wv_buyouts.geojson` | 2,826 points, years 1988 to 2019 | Program and year per property |
| Repetitive loss areas | `wv_repetitive_loss.geojson` | 55 polygons | FEMA-designated repetitive loss areas |
| HUC-8 watersheds | `wv_watersheds.geojson` | 33 watersheds | 8 Chesapeake (HUC 02), 25 Ohio (HUC 05) |
| FEMA SFHA floodplain | `wv_floodplain.geojson` | Special Flood Hazard Area | Statewide multipolygon, 798 sq mi |

All source files are in `atlas-of-accountability-v4 wv/data`.

---

## Validation

- All **2,826 buyout points** fell inside a WV county. Zero unmatched.
- All **55 repetitive-loss areas** placed. They fall in only **11 of 55 counties**.
- `FLOOD_EAL_TOTAL` and `FLOOD_RISK_SCORE` reproduce `wv_nri_flood.geojson` (`feal`, `frisk`) exactly on all 55 counties, confirming that file is a derived extract of the NRI county file.
- County areas sum to 24,475 sq mi against West Virginia's ~24,230. The 1% excess is expected from polygon generalization.
- SFHA totals 781 sq mi across counties, **3.2% of the state**.

---

## Columns

### Identity
`GEOID` (5-digit FIPS, zero-padded, join on this), `COUNTY`, `STATE`.

### Atlas of Accountability core (2011 to 2024)
| Column | Notes |
|---|---|
| `DISASTER_COUNT_2011_2024` | Federal major disaster declarations |
| `FEMA_PA_HM` | FEMA Public Assistance + Hazard Mitigation, dollars |
| `FEMA_PER_CAPITA`, `POPULATION` | |
| `CDC_SVI_2022` | CDC Social Vulnerability Index, 0 to 1 |
| `OMB_CLASS` | Urban / Rural |
| `SAIDI_MIN_AVG`, `SAIDI_MIN_MAX` | Annual power-outage minutes, 2023 |
| `PCT_POP_60PLUS`, `AGE_CLASS` | Older adults. **Note:** this percent is rounded to 1dp; do not threshold on it |
| `PCT_MINORITY` | Share who are people of color, CDC SVI 2022 |
| `HEAT_NRI` | Heat National Risk Index, 0 to 100 |
| `COMPOUND_RISK_COUNT_NATL` | The **national** 0-to-4 compound score from the Atlas master. Its thresholds are national quartiles, so within WV it discriminates weakly. |

### FEMA National Risk Index, composite
`NRI_POP_2020`, `NRI_AREA_SQMI`, `NRI_BUILDING_VALUE`, `NRI_AGRICULTURE_VALUE`,
`NRI_SCORE_COMPOSITE`, `NRI_RATING_COMPOSITE`, `NRI_EAL_TOTAL_COMPOSITE`,
`NRI_SOVI_SCORE`, `NRI_SOVI_RATING`, `NRI_RESILIENCE_SCORE`, `NRI_RESILIENCE_RATING`.

NRI ratings are relative and read: Very Low, Relatively Low, Relatively Moderate, Relatively High, Very High.

### NRI, inland flooding
FEMA calls the hazard **Inland Flooding** (not "riverine").

| Column | Notes |
|---|---|
| `FLOOD_RISK_SCORE`, `FLOOD_RISK_RATING` | Hazard Type Risk Index |
| `FLOOD_EAL_TOTAL` | Expected Annual Loss, dollars per year |
| `FLOOD_EAL_SCORE`, `FLOOD_EAL_RATING` | |
| `FLOOD_EAL_NATL_PCTILE` | **National** percentile of the loss rate. This is where WV counties look far worse than their in-state ratings suggest. |
| `FLOOD_EVENTS`, `FLOOD_ANNUAL_FREQ` | Historic event count and annualized frequency |
| `FLOOD_IMPACTED_AREA_SQMI`, `FLOOD_EXPOSURE_TOTAL` | |
| `FLOOD_HIST_LOSS_RATING` | Historic loss ratio rating |

### FEMA SFHA floodplain
| Column | Notes |
|---|---|
| `SFHA_AREA_SQMI` | Area of the county inside the Special Flood Hazard Area |
| `PCT_COUNTY_IN_SFHA` | That area as a share of county area. Mason leads at 9.85%. |

### Buyouts
| Column | Notes |
|---|---|
| `BUYOUTS_TOTAL` | All buyout properties in the county |
| `BUYOUTS_FEMA`, `BUYOUTS_USACE`, `BUYOUTS_NRCS`, `BUYOUTS_HUD`, `BUYOUTS_COMMUNITY` | By funding program |
| `BUYOUT_YEAR_MIN`, `BUYOUT_YEAR_MAX` | Year range where recorded |

**Limitations.** The source `comm` field mixes county names ("McDowell County*") with place names ("Welch"), so it is not a usable county key. Points were **spatially joined** to county polygons instead. **The `yr` field is blank for 1,264 of 2,826 points (45%)**, so year ranges are partial and buyout counts must not be presented as a time series. 39 points are marked program "FEMA?" and were counted as FEMA.

### Repetitive loss
| Column | Notes |
|---|---|
| `REPETITIVE_LOSS_AREAS` | Count of FEMA repetitive-loss areas |
| `REPETITIVE_LOSS_STREAMS` | Named streams driving them |

Only **11 of 55 counties** have any. Morgan (9), Greenbrier (8), Jefferson (7), Berkeley (6).

### Watershed and basin
| Column | Notes |
|---|---|
| `PRIMARY_WATERSHED`, `PRIMARY_HUC8` | Largest-overlap HUC-8 |
| `BASIN` | Chesapeake Bay (HUC 02) or Ohio River (HUC 05) |
| `SPANS_BOTH_BASINS` | Y only where a second basin covers **at least 1%** of the county |
| `ALL_WATERSHEDS` | Every HUC-8 overlapping the county by 1% or more |

**The 1% threshold matters.** Without it, all 8 Eastern Panhandle counties read as spanning both basins on 0.0 to 0.2% slivers along the continental divide. That is a geometry artifact. With the threshold, exactly **one** county genuinely spans: **Monroe**, which reaches the Upper James.

**Basin split:** 8 Chesapeake counties (Berkeley, Grant, Hampshire, Hardy, Jefferson, Mineral, Morgan, Pendleton) and 47 Ohio River counties.

---

## What is NOT in this file

This master covers **hazard, flood, and exposure**. It does not contain:

- Land-use or extractive-industry layers (mining permits, abandoned mine lands, oil and gas wells, pipelines)
- Energy-infrastructure layers (generating stations, large-load facilities)
- Environmental contamination (Superfund, brownfields, coal ash impoundments, water quality violations)
- Landownership records

Any analysis of how flood risk intersects those subjects requires data that is not in this repository.

**On the basin columns.** They record *which* basin a county sits in. They do not carry any federal watershed-program funding figures, so they can show the split and not the dollars.
