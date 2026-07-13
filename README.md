# Atlas of Disaster: West Virginia

County-level flood, hazard, and disaster data for all 55 West Virginia counties. Part of the [Atlas of Disaster](https://rebuildbydesign.org/atlas-of-disaster/) by [Rebuild by Design](https://rebuildbydesign.org).

This is a **data repository**. It is not the WV map site (that is [`Westvirginia-atlas`](https://github.com/rebuildbydesign/Westvirginia-atlas)).

---

## What is here

**`data/wv_county_master.csv`** is the point of the repo: one row per WV county, 55 columns, joining every layer below on 5-digit FIPS.

Open **`index.html`** in a browser for a sortable, filterable view of all 55 counties.

| File | What it is |
|---|---|
| `data/wv_county_master.csv` | **The master file.** 55 counties, 55 columns. |
| `data/Atlas_FEMA_WV.geojson` | Atlas of Accountability core, WV subset (55 counties, 41 properties): disaster declarations 2011 to 2024, FEMA PA+HM, CDC SVI, SAIDI, older adults, race, heat NRI. |
| `data/US_Congress_WV.geojson` | WV congressional districts (2). |
| `data/NRI_Counties_WV.geojson` | FEMA National Risk Index, county level. 467 fields. |
| `data/wv_buyouts.geojson` | 2,826 buyout properties (FEMA, USACE, NRCS, HUD, community). |
| `data/wv_repetitive_loss.geojson` | 55 FEMA repetitive-loss areas. |
| `data/wv_floodplain.geojson` | FEMA Special Flood Hazard Area, statewide. |
| `data/wv_watersheds.geojson` | 33 HUC-8 watersheds. |
| `data/wv_nri_flood.geojson` | Flood extract derived from the NRI county file. |
| `docs/DATA_DICTIONARY.md` | **Read this before using the data.** Every column, source, and limitation. |
| `tools/build_wv_master.py` | Regenerates the master file from the layers in `data/`. |

## Rebuilding the master file

```bash
pip install shapely pyproj
python3 tools/build_wv_master.py
```

Area math runs in EPSG:5070 (CONUS Albers equal-area). Source GeoJSONs are EPSG:4326.

---

## What the data shows

- **Mason County has the highest annual outage duration in the state** (854 SAIDI minutes per year, against 760 for the next tier) **and the largest share of any county inside the FEMA Special Flood Hazard Area (9.85%)**.
- **Buyouts are not distributed like disaster declarations.** McDowell County holds **708 of the state's 2,826 buyout properties**, more than double any other county, despite 3 disaster declarations and under 1% of its area in the floodplain.
- **Repetitive loss is concentrated in 11 of 55 counties.** Morgan (9), Greenbrier (8), Jefferson (7), Berkeley (6).
- **The basin split is 47 Ohio River counties to 8 Chesapeake Bay counties.** The Chesapeake counties are Berkeley, Grant, Hampshire, Hardy, Jefferson, Mineral, Morgan, and Pendleton. Only Monroe County genuinely spans both basins.

---

## Known limitations

Read `docs/DATA_DICTIONARY.md` in full. The two that matter most:

**Buyout years are missing for 1,264 of 2,826 properties (45%).** Buyout counts are reliable. A buyout **time series is not**, and would mislead.

**This repo covers hazard, flood, and exposure only.** It does not contain land-use, energy-infrastructure, extractive-industry, or landownership layers. Any analysis of how flood risk intersects those subjects requires data that is not here.

**The census-tract NRI file is not included.** It is 46MB and nothing here reads it. Add it via Git LFS if tract-level analysis begins.

---

## Sources

- **FEMA National Risk Index**, county level
- **FEMA OpenFEMA**: major disaster declarations, Public Assistance, Hazard Mitigation, 2011 to 2024
- **FEMA National Flood Hazard Layer** (Special Flood Hazard Area) and repetitive-loss areas
- **FEMA, USACE, NRCS, HUD** buyout property records
- **USGS** HUC-8 watershed boundaries
- **CDC Social Vulnerability Index**, 2022
- **U.S. Census Bureau**, ACS 5-Year Estimates
- **SAIDI**, 2023 power reliability

## Related

- [Atlas of Accountability](https://rebuildbydesign.github.io/atlas-of-accountability-v2/) (national interactive map)
- [Atlas of Disaster](https://rebuildbydesign.org/atlas-of-disaster/)
