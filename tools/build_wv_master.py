#!/usr/bin/env python3
"""
West Virginia county master file.

One row per WV county (55), keyed on 5-digit FIPS. Joins:
  - Atlas of Accountability core   <- Master/atlas_county_master.csv (WV subset)
  - FEMA National Risk Index       <- NRI_Counties_WV.geojson (467 fields, subset kept)
  - FEMA/USACE/NRCS/HUD buyouts    <- wv_buyouts.geojson (2,826 points, spatial join)
  - Repetitive loss areas          <- wv_repetitive_loss.geojson (55 areas)
  - HUC-8 watersheds + basin       <- wv_watersheds.geojson (33 watersheds, spatial)
  - FEMA SFHA floodplain           <- wv_floodplain.geojson (statewide, area intersect)

Area math is done in EPSG:5070 (CONUS Albers equal-area). Source geojsons are EPSG:4326.
"""
import json, csv, os, collections
from shapely.geometry import shape, Point
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree
from pyproj import Transformer

# Repo-relative. Run from anywhere: python3 tools/build_wv_master.py
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WV = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "data")

# Atlas core is read from the WV subset of the national Atlas geojson, so this
# repo is self-contained. The national master CSV lives in the ATLAS V3 UPDATE
# workspace and is not required here.
ATLAS_GEOJSON = os.path.join(ROOT, "data", "Atlas_FEMA_WV.geojson")

TO_ALBERS = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True).transform
SQM_TO_SQMI = 1 / 2_589_988.11


def load(fn):
    return json.load(open(os.path.join(WV, fn)))["features"]


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- counties
nri = load("NRI_Counties_WV.geojson")
counties = {}
for f in nri:
    p = f["properties"]
    fips = str(p["State-County FIPS Code"]).zfill(5)
    geom = shape(f["geometry"])
    counties[fips] = {
        "props": p,
        "geom_ll": geom,                       # lon/lat, for spatial joins
        "geom_ea": transform(TO_ALBERS, geom),  # equal-area, for area math
    }
print(f"counties: {len(counties)}")

fips_list = list(counties)
geoms_ll = [counties[f]["geom_ll"] for f in fips_list]
tree = STRtree(geoms_ll)

# ---------------------------------------------------------------- buyouts
# The `comm` field mixes county names ("McDowell County*") with place names
# ("Welch"), so it is not a reliable county key. Spatial-join the points instead.
buy = collections.defaultdict(lambda: collections.Counter())
buy_years = collections.defaultdict(list)
unmatched = 0
for f in load("wv_buyouts.geojson"):
    pt = Point(f["geometry"]["coordinates"][:2])
    hits = tree.query(pt)
    fips = None
    for i in hits:
        if geoms_ll[i].contains(pt):
            fips = fips_list[i]
            break
    if fips is None:
        unmatched += 1
        continue
    prog = (f["properties"].get("prog") or "Unknown").strip().rstrip("?") or "Unknown"
    buy[fips][prog] += 1
    buy[fips]["TOTAL"] += 1
    y = num(f["properties"].get("yr"))
    if y:
        buy_years[fips].append(int(y))
print(f"buyouts joined: {sum(v['TOTAL'] for v in buy.values()):,}  unmatched (outside WV): {unmatched}")

# ---------------------------------------------------------------- repetitive loss
rl = collections.Counter()
rl_streams = collections.defaultdict(set)
name_to_fips = {counties[f]["props"]["County Name"]: f for f in counties}
for f in load("wv_repetitive_loss.geojson"):
    p = f["properties"]
    fips = name_to_fips.get(p["County"])
    if fips:
        rl[fips] += 1
        if p.get("Stream_Name"):
            rl_streams[fips].add(p["Stream_Name"])
print(f"repetitive-loss areas: {sum(rl.values())} across {len(rl)} counties")

# ---------------------------------------------------------------- watersheds
# Basin from HUC-8 prefix: 02 = Mid-Atlantic (Chesapeake Bay Program),
# 05 = Ohio River Basin. This is the federal-watershed-funding gap.
ws = []
for f in load("wv_watersheds.geojson"):
    p = f["properties"]
    huc = str(p["huc"])
    ws.append({
        "name": p["name"], "huc": huc,
        "basin": "Chesapeake Bay" if huc.startswith("02") else ("Ohio River" if huc.startswith("05") else "Other"),
        "geom": transform(TO_ALBERS, shape(f["geometry"])),
    })
print(f"watersheds: {len(ws)}  ({sum(1 for w in ws if w['basin']=='Chesapeake Bay')} Chesapeake, "
      f"{sum(1 for w in ws if w['basin']=='Ohio River')} Ohio)")

# ---------------------------------------------------------------- floodplain (SFHA)
# The FEMA SFHA multipolygon is not topologically valid (self-intersections at
# shared boundaries). Repair each part with make_valid before unioning, or GEOS
# raises a side-location conflict.
from shapely import make_valid
parts = []
for f in load("wv_floodplain.geojson"):
    g = transform(TO_ALBERS, shape(f["geometry"]))
    if not g.is_valid:
        g = make_valid(g)
    parts.append(g)
sfha = unary_union(parts)
if not sfha.is_valid:
    sfha = make_valid(sfha)
print(f"SFHA floodplain: {sfha.area * SQM_TO_SQMI:,.0f} sq mi statewide")

# ---------------------------------------------------------------- Atlas core
OA = "county-level-older-adults_"
atlas = {}
for f in json.load(open(ATLAS_GEOJSON))["features"]:
    p = f["properties"]
    atlas[p["GEOID"]] = {
        "COUNTY_DISASTER_COUNT": p.get("COUNTY_DISASTER_COUNT"),
        "COUNTY_TOTAL_FEMA": p.get("COUNTY_TOTAL_FEMA"),
        "COUNTY_PER_CAPITA": p.get("COUNTY_PER_CAPITA"),
        "COUNTY_POPULATION": p.get("COUNTY_POPULATION"),
        "CDC_SVI_2022": p.get("CDC SVI (2022)"),
        "OMB_CLASS": p.get("OMB_CLASS"),
        "SAIDI_MIN_AVG": p.get("SAIDI_MIN_AVG"),
        "SAIDI_MIN_MAX": p.get("SAIDI_MIN_MAX"),
        "PCT_POP_60PLUS": p.get(OA + "PCT POP 60+"),
        "AGE_CLASS": p.get(OA + "AGE CLASS"),
        "COUNTY_PCT_MINORITY": p.get("COUNTY_PCT_MINORITY"),
        "HEAT_NRI": p.get("HEAT_NRI"),
        "COMPOUND_RISK_COUNT": p.get("COMPOUND_RISK_COUNT_NATL"),
    }
print(f"atlas core rows for WV: {len(atlas)}")

# ---------------------------------------------------------------- build
COLS = [
    "GEOID", "COUNTY", "STATE",
    # Atlas of Accountability core
    "DISASTER_COUNT_2011_2024", "FEMA_PA_HM", "FEMA_PER_CAPITA", "POPULATION",
    "CDC_SVI_2022", "OMB_CLASS", "SAIDI_MIN_AVG", "SAIDI_MIN_MAX",
    "PCT_POP_60PLUS", "AGE_CLASS", "PCT_MINORITY", "HEAT_NRI",
    "COMPOUND_RISK_COUNT_NATL",
    # FEMA National Risk Index, composite
    "NRI_POP_2020", "NRI_AREA_SQMI", "NRI_BUILDING_VALUE", "NRI_AGRICULTURE_VALUE",
    "NRI_SCORE_COMPOSITE", "NRI_RATING_COMPOSITE", "NRI_EAL_TOTAL_COMPOSITE",
    "NRI_SOVI_SCORE", "NRI_SOVI_RATING", "NRI_RESILIENCE_SCORE", "NRI_RESILIENCE_RATING",
    # NRI, inland flooding
    "FLOOD_RISK_SCORE", "FLOOD_RISK_RATING", "FLOOD_EAL_TOTAL",
    "FLOOD_EAL_SCORE", "FLOOD_EAL_RATING", "FLOOD_EAL_NATL_PCTILE",
    "FLOOD_EVENTS", "FLOOD_ANNUAL_FREQ", "FLOOD_IMPACTED_AREA_SQMI",
    "FLOOD_EXPOSURE_TOTAL", "FLOOD_HIST_LOSS_RATING",
    # FEMA SFHA floodplain
    "SFHA_AREA_SQMI", "PCT_COUNTY_IN_SFHA",
    # Buyouts
    "BUYOUTS_TOTAL", "BUYOUTS_FEMA", "BUYOUTS_USACE", "BUYOUTS_NRCS",
    "BUYOUTS_HUD", "BUYOUTS_COMMUNITY", "BUYOUT_YEAR_MIN", "BUYOUT_YEAR_MAX",
    # Repetitive loss
    "REPETITIVE_LOSS_AREAS", "REPETITIVE_LOSS_STREAMS",
    # Watershed / basin
    "PRIMARY_WATERSHED", "PRIMARY_HUC8", "BASIN", "SPANS_BOTH_BASINS", "ALL_WATERSHEDS",
]

rows = []
for fips, c in sorted(counties.items()):
    p = c["props"]
    a = atlas.get(fips, {})
    ea = c["geom_ea"]
    area_sqmi = ea.area * SQM_TO_SQMI

    # SFHA intersection
    try:
        inter = ea.intersection(sfha)
        sfha_sqmi = inter.area * SQM_TO_SQMI
    except Exception:
        sfha_sqmi = None

    # Watershed overlap. Require at least 1% of the county's area to count.
    # Without this, all 8 Eastern Panhandle counties read as spanning both basins
    # on 0.0-0.2% slivers along the continental divide, which is a geometry
    # artifact, not a fact about the county.
    MIN_OVERLAP = 0.01
    ovl = []
    for w in ws:
        try:
            ia = ea.intersection(w["geom"]).area
        except Exception:
            ia = 0
        if ia / ea.area >= MIN_OVERLAP:
            ovl.append((ia, w))
    ovl.sort(key=lambda x: -x[0])
    basins = {w["basin"] for _, w in ovl}
    primary = ovl[0][1] if ovl else None

    b = buy.get(fips, collections.Counter())
    yrs = buy_years.get(fips, [])

    rows.append({
        "GEOID": fips,
        "COUNTY": p["County Name"],
        "STATE": "West Virginia",
        "DISASTER_COUNT_2011_2024": a.get("COUNTY_DISASTER_COUNT", ""),
        "FEMA_PA_HM": a.get("COUNTY_TOTAL_FEMA", ""),
        "FEMA_PER_CAPITA": a.get("COUNTY_PER_CAPITA", ""),
        "POPULATION": a.get("COUNTY_POPULATION", ""),
        "CDC_SVI_2022": a.get("CDC_SVI_2022", ""),
        "OMB_CLASS": a.get("OMB_CLASS", ""),
        "SAIDI_MIN_AVG": a.get("SAIDI_MIN_AVG", ""),
        "SAIDI_MIN_MAX": a.get("SAIDI_MIN_MAX", ""),
        "PCT_POP_60PLUS": a.get("PCT_POP_60PLUS", ""),
        "AGE_CLASS": a.get("AGE_CLASS", ""),
        "PCT_MINORITY": a.get("COUNTY_PCT_MINORITY", ""),
        "HEAT_NRI": a.get("HEAT_NRI", ""),
        "COMPOUND_RISK_COUNT_NATL": a.get("COMPOUND_RISK_COUNT", ""),
        "NRI_POP_2020": p.get("Population (2020)"),
        "NRI_AREA_SQMI": round(num(p.get("Area (sq mi)")) or 0, 2),
        "NRI_BUILDING_VALUE": p.get("Building Value ($)"),
        "NRI_AGRICULTURE_VALUE": p.get("Agriculture Value ($)"),
        "NRI_SCORE_COMPOSITE": round(num(p.get("National Risk Index - Score - Composite")) or 0, 2),
        "NRI_RATING_COMPOSITE": p.get("National Risk Index - Rating - Composite"),
        "NRI_EAL_TOTAL_COMPOSITE": round(num(p.get("Expected Annual Loss - Total - Composite")) or 0),
        "NRI_SOVI_SCORE": round(num(p.get("Social Vulnerability - Score")) or 0, 2),
        "NRI_SOVI_RATING": p.get("Social Vulnerability - Rating"),
        "NRI_RESILIENCE_SCORE": round(num(p.get("Community Resilience - Score")) or 0, 2),
        "NRI_RESILIENCE_RATING": p.get("Community Resilience - Rating"),
        "FLOOD_RISK_SCORE": round(num(p.get("Inland Flooding - Hazard Type Risk Index Score")) or 0, 2),
        "FLOOD_RISK_RATING": p.get("Inland Flooding - Hazard Type Risk Index Rating"),
        "FLOOD_EAL_TOTAL": round(num(p.get("Inland Flooding - Expected Annual Loss - Total")) or 0),
        "FLOOD_EAL_SCORE": round(num(p.get("Inland Flooding - Expected Annual Loss Score")) or 0, 2),
        "FLOOD_EAL_RATING": p.get("Inland Flooding - Expected Annual Loss Rating"),
        "FLOOD_EAL_NATL_PCTILE": round(num(p.get("Inland Flooding - Expected Annual Loss Rate - National Percentile")) or 0, 2),
        "FLOOD_EVENTS": p.get("Inland Flooding - Number of Events"),
        "FLOOD_ANNUAL_FREQ": round(num(p.get("Inland Flooding - Annualized Frequency")) or 0, 3),
        "FLOOD_IMPACTED_AREA_SQMI": round(num(p.get("Inland Flooding - Exposure - Impacted Area (sq mi)")) or 0, 2),
        "FLOOD_EXPOSURE_TOTAL": round(num(p.get("Inland Flooding - Exposure - Total")) or 0),
        "FLOOD_HIST_LOSS_RATING": p.get("Inland Flooding - Historic Loss Ratio - Total Rating"),
        "SFHA_AREA_SQMI": round(sfha_sqmi, 2) if sfha_sqmi is not None else "",
        "PCT_COUNTY_IN_SFHA": round(sfha_sqmi / area_sqmi * 100, 2) if sfha_sqmi and area_sqmi else "",
        "BUYOUTS_TOTAL": b.get("TOTAL", 0),
        "BUYOUTS_FEMA": b.get("FEMA", 0),
        "BUYOUTS_USACE": b.get("USACE", 0),
        "BUYOUTS_NRCS": b.get("NRCS", 0),
        "BUYOUTS_HUD": b.get("HUD", 0),
        "BUYOUTS_COMMUNITY": b.get("Community", 0),
        "BUYOUT_YEAR_MIN": min(yrs) if yrs else "",
        "BUYOUT_YEAR_MAX": max(yrs) if yrs else "",
        "REPETITIVE_LOSS_AREAS": rl.get(fips, 0),
        "REPETITIVE_LOSS_STREAMS": "; ".join(sorted(rl_streams.get(fips, []))),
        "PRIMARY_WATERSHED": primary["name"] if primary else "",
        "PRIMARY_HUC8": primary["huc"] if primary else "",
        "BASIN": primary["basin"] if primary else "",
        "SPANS_BOTH_BASINS": "Y" if len(basins - {"Other"}) > 1 else "N",
        "ALL_WATERSHEDS": "; ".join(w["name"] for _, w in ovl),
    })

path = os.path.join(OUT, "wv_county_master.csv")
with open(path, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLS})
print(f"\nwrote {path}  ({len(rows)} rows, {len(COLS)} cols)")
