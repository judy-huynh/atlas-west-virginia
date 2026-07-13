# Methodology: how each column was produced

Written 2026-07-13. Companion to `DATA_DICTIONARY.md`.

This file answers one question for every column: **did it come from a source, or did I calculate it?**

---

## Summary

| Column group | Origin |
|---|---|
| Disaster count, FEMA PA+HM, population, per capita, SVI, SAIDI, older adults, race, heat NRI | **From source.** Atlas of Accountability. Not calculated here. |
| Flood risk score, flood rating, flood EAL, flood events, flood frequency, all NRI fields | **From source.** FEMA National Risk Index, county file. Not calculated here. |
| Buyout counts by program | **Calculated.** Spatial join of 2,826 points to county polygons. |
| Repetitive-loss area counts | **Calculated.** Grouped by the `County` attribute already on each area. |
| SFHA area, % of county in floodplain | **Calculated.** Polygon intersection. **Did not exist at county level in any source.** |
| Watershed, basin, spans-both-basins | **Calculated.** Polygon overlap, with a 1% minimum threshold. |

---

## The direct answer to "was the floodplain percentage in the GIS, or did you calculate it?"

**I calculated it. It was not in the GIS at county level.**

`wv_floodplain.geojson` is a **single statewide MultiPolygon** with exactly one attribute: `zone = SFHA`. It has no county field, no area field, and no percentages. There was no county-level floodplain table anywhere in the data folder. To get a per-county number I had to intersect the floodplain polygon with each county polygon and measure the resulting area.

## What year is the floodplain? Unknown, and this matters

**The file carries no date, no source, and no zone breakdown.** Its only property is `zone = SFHA`. There is no effective date, no NFHL panel reference, no A/AE/VE zone distinction, and no CRS declaration. The file was last modified on 2026-06-20, which tells us when it was saved, not what it represents.

**What "SFHA" means:** FEMA's Special Flood Hazard Area is by definition the **1% annual chance floodplain**, which is what people call the "100-year floodplain." So conceptually, yes, that is what this is measuring.

**What I cannot tell you:**
- Which NFHL vintage it was pulled from
- Whether it includes all SFHA zones or only some
- Whether unmapped or approximate-study areas were included or dropped
- Whether the geometry was simplified before it reached this folder

Your own concept note has the rule for this: *"Every layer needs a source and a date. If you can't find both, ask Judy before using it."* This layer has neither. **Before any floodplain number is published, the source and vintage need to be confirmed with whoever produced this file.** The percentages are internally consistent and the math is sound, but the provenance is not established, and I am not going to assert a year I cannot see.

The same gap applies to `wv_buyouts.geojson`, `wv_repetitive_loss.geojson`, and `wv_watersheds.geojson`. None carry a source or date. The NRI file is the only layer that self-documents: it declares **`National Risk Index Version = December 2025`**.

---

## Per-field method

### `BUYOUTS_TOTAL` and the per-program columns (calculated)

Source: `wv_buyouts.geojson`, 2,826 **point** features. Properties: `comm`, `prog`, `yr`, `ncomm`.

**Method.** Point-in-polygon spatial join of each buyout point to the 55 county polygons, then counted by `prog`.

**Why spatial and not by name.** The `comm` field mixes county names ("McDowell County*") with place names ("Welch", "Wyoming County*"). 111 distinct values, only 1,362 of 2,826 points containing the word "County". It is not a usable county key. The geometry is.

**Result.** All 2,826 points fell inside a WV county. Zero unmatched, which is itself a check that the join is correct.

**Program mapping.** FEMA 1,565, Community 716, USACE 247, NRCS 184, HUD 74, and 39 marked `FEMA?` which I counted as FEMA. That last decision is a judgment call and is reversible.

**Limitation.** `yr` is blank for **1,264 of 2,826 (45%)**. `BUYOUT_YEAR_MIN` / `MAX` describe only the 55% with a year. **Do not build a buyout time series from this.**

### `REPETITIVE_LOSS_AREAS` and `REPETITIVE_LOSS_STREAMS` (calculated, but trivially)

Source: `wv_repetitive_loss.geojson`, 55 polygon features, each already carrying a `County` attribute.

**Method.** Grouped by the existing `County` field and counted. This is a plain count, not a spatial operation, because the source already assigns each area to a county. Stream names concatenated from `Stream_Name`.

**Result.** 55 areas across only **11 of 55 counties**. Morgan 9, Greenbrier 8, Jefferson 7, Berkeley 6.

**Note.** These are repetitive-loss **areas**, not repetitive-loss **properties**. They are not a count of flooded homes.

### `SFHA_AREA_SQMI` and `PCT_COUNTY_IN_SFHA` (calculated)

Source: `wv_floodplain.geojson`, one statewide MultiPolygon.

**Method.**
1. Reprojected both the floodplain and the county polygons from EPSG:4326 to **EPSG:5070** (CONUS Albers equal-area). Area cannot be measured correctly in lat/lon degrees; it must be done in an equal-area projection.
2. The floodplain MultiPolygon is **not topologically valid** (self-intersections at shared boundaries, which is common for FEMA flood layers). GEOS refused to union it. Repaired each part with `make_valid` before dissolving.
3. Intersected the repaired floodplain with each county polygon.
4. `SFHA_AREA_SQMI` = area of that intersection. `PCT_COUNTY_IN_SFHA` = that divided by the county's own area from the same equal-area projection.

**Cross-check.** County areas sum to 24,475 sq mi against West Virginia's actual ~24,230, about 1% over, which is the expected error from polygon generalization. SFHA totals 781 sq mi, **3.2% of the state**.

**Caveat.** The percentage is only as good as the floodplain layer, whose vintage is unknown. See above.

### `FLOOD_RISK_SCORE`, `FLOOD_RISK_RATING`, `FLOOD_EAL_TOTAL`, and all `FLOOD_*` columns (from source, not calculated)

Source: `NRI_Counties_WV.geojson`, **FEMA National Risk Index, version December 2025**.

**I did not compute any of these.** They are lifted directly from FEMA's fields, renamed for readability:

| Our column | FEMA's field |
|---|---|
| `FLOOD_RISK_SCORE` | `Inland Flooding - Hazard Type Risk Index Score` |
| `FLOOD_RISK_RATING` | `Inland Flooding - Hazard Type Risk Index Rating` |
| `FLOOD_EAL_TOTAL` | `Inland Flooding - Expected Annual Loss - Total` |
| `FLOOD_EAL_SCORE` / `_RATING` | `Inland Flooding - Expected Annual Loss Score` / `Rating` |
| `FLOOD_EAL_NATL_PCTILE` | `Inland Flooding - Expected Annual Loss Rate - National Percentile` |
| `FLOOD_EVENTS` | `Inland Flooding - Number of Events` |
| `FLOOD_ANNUAL_FREQ` | `Inland Flooding - Annualized Frequency` |

**"Flood loss per year" is FEMA's Expected Annual Loss**, an actuarial estimate of average annual dollar loss from inland flooding. It is FEMA's model output, not an observed figure and not my arithmetic.

FEMA calls the hazard **Inland Flooding**, not "riverine." The event record is about **28 years deep** (for example, 40 events at an annualized frequency of 1.4286).

**Validation.** These columns reproduce `wv_nri_flood.geojson` (`frisk`, `feal`) **exactly on all 55 counties**, which also proves that file is a derived extract of the NRI county file rather than an independent source.

**Important.** NRI ratings (Very Low, Relatively Low, Relatively Moderate, Relatively High, Very High) are **relative**. A WV county rated "Relatively Low" can still sit in a high **national** percentile on loss rate. Use `FLOOD_EAL_NATL_PCTILE` when comparing WV against the country, not the rating.

### `PRIMARY_WATERSHED`, `BASIN`, `SPANS_BOTH_BASINS` (calculated)

Source: `wv_watersheds.geojson`, 33 HUC-8 polygons.

**Method.** Overlapped each county with each watershed in EPSG:5070. `PRIMARY_WATERSHED` is the largest-overlap HUC-8. `BASIN` is derived from the HUC-8 prefix: **02 = Mid-Atlantic (Chesapeake Bay), 05 = Ohio River**.

**The 1% threshold.** An overlap must cover at least 1% of the county's area to count. Without this, all 8 Eastern Panhandle counties read as spanning both basins on 0.0 to 0.2% slivers along the continental divide, which is a geometry artifact and not a fact. With the threshold, exactly **one** county genuinely spans: **Monroe**, which reaches the Upper James.

### Everything else (from source)

`DISASTER_COUNT_2011_2024`, `FEMA_PA_HM`, `FEMA_PER_CAPITA`, `POPULATION`, `CDC_SVI_2022`, `OMB_CLASS`, `SAIDI_MIN_AVG/MAX`, `PCT_POP_60PLUS`, `AGE_CLASS`, `PCT_MINORITY`, `HEAT_NRI`, `COMPOUND_RISK_COUNT_NATL` all come from the Atlas of Accountability, via `Atlas_FEMA_WV.geojson`.

Disaster counts and FEMA totals were **fact-checked against the FINAL Atlas of Accountability 2011-2024 Workbook, `County Level 2024` tab, and reconcile exactly on all 55 counties.** See the correction note in `DATA_DICTIONARY.md`.

---

## Reproducing all of it

```bash
pip install shapely pyproj
python3 tools/build_wv_master.py
```

Every calculated column is produced by that one script. Nothing was done by hand, in Excel, or in QGIS, so there are no manual steps to trust.

---

## Open questions before publication

1. **What is the vintage and source of `wv_floodplain.geojson`?** Unknown. Blocks publishing any floodplain percentage.
2. **Same for buyouts, repetitive loss, and watersheds.** No source or date on any of them.
3. **Are the 39 `FEMA?` buyout records FEMA?** I counted them as FEMA.
4. **Are repetitive-loss areas current?** No date on the layer.
