# Atlas of Disaster: West Virginia

**West Virginia floods worse than almost anywhere in the country, and almost nobody has the numbers to prove it.**

This project puts them in one place, for all 55 counties, so that the people making decisions about West Virginia can see what the state is actually carrying.

Part of the [Atlas of Disaster](https://rebuildbydesign.org/atlas-of-disaster/) by [Rebuild by Design](https://rebuildbydesign.org).

**→ [Open the County Risk Profile](https://judy-huynh.github.io/atlas-west-virginia/)**

---

## Why this exists

West Virginia rarely appears in national climate risk work. It is small, it is rural, and its counties do not produce the headline damage totals that put a place on a map. So the data gets collected, the state gets averaged away, and the funding follows the places that were easy to see.

The consequence is not just that West Virginia is overlooked. It is that **the tools meant to measure risk actively make the state look safer than it is.**

FEMA rates every county's flood risk *relative to the whole United States*. In a state where flooding is everywhere, that comparison flattens. The result is that FEMA labels **7 West Virginia counties "Relatively Low" flood risk that are, in fact, in the worst 1% of counties in the country** for flood losses. Clay, Gilmer, Lewis, Pleasants, Tyler, Webster, and Wirt. Pleasants and Wirt sit at the 99.9th percentile nationally, and carry a label that tells a grant reviewer not to worry about them.

That is the gap this repository exists to close.

---

## Where West Virginia stands

The findings live on the site, not in this file, so they are computed from the data and cannot go stale.

**→ [Read the findings](https://judy-huynh.github.io/atlas-west-virginia/findings.html)**

In short: the median West Virginia county sits in the 96th percentile nationally for flood loss, the state loses hundreds of millions of dollars a year to flooding, and the counties hit hardest have received the least federal money. FEMA's own rating hides all of it.

---

## Who this is for

The data is built to be used by people who have to justify a decision:

- **Policymakers and state agencies**, who need to show the scale of the gap between what the state is losing and what it has to spend.
- **Emergency management**, who need to know where a flood becomes a crisis the county cannot handle alone.
- **City and municipal planners**, who need to know where the water is before siting a school, clinic, or fire station.
- **Communities and advocates**, who need evidence for a county that no national dataset has ever bothered to look at.

The [Compound Risk Explorer](https://judy-huynh.github.io/atlas-west-virginia/explore.html) lets each of them ask their own question of the same data, and **click any county to get a sourced paragraph** they can put straight into an application or a briefing.

---

## What this is not, yet

Being clear about the limits is part of the point.

**This covers flooding, hazard, and vulnerability.** It does not yet contain data centers, coal plants, mining permits, abandoned mine lands, Superfund sites, or landownership. Those are coming, and they answer a different question: not *what threatens this county*, but *who is putting it there*. Until they are here, this data cannot speak to that.

**Some source layers arrived without a date.** The flood zone, buyout, repetitive loss, and watershed files carry no vintage in them. The measurements are sound; the provenance needs confirming before any floodplain figure is published. See [About the data](https://judy-huynh.github.io/atlas-west-virginia/methodology.html).

**Never sum the disaster column.** One storm is declared across many counties at once. West Virginia has had **23** federal disaster declarations, 2011 to 2024. The county column says how many of those touched each county; adding it up counts the same storm over and over.

---

## The pages

| Page | What it does |
|---|---|
| **[Findings](https://judy-huynh.github.io/atlas-west-virginia/findings.html)** | Where West Virginia actually stands. Every figure computed live from the data. |
| **[County Risk Profile](https://judy-huynh.github.io/atlas-west-virginia/)** | All 55 counties, every column, sortable. |
| **[Compound Risk Explorer](https://judy-huynh.github.io/atlas-west-virginia/explore.html)** | Filter by the risks that matter to your work. Click a county for a sourced evidence paragraph. |
| **[About the data](https://judy-huynh.github.io/atlas-west-virginia/methodology.html)** | What every column means and where it comes from. |

---

## The data

**`data/wv_county_profile.csv`** is the master file: one row per county, 56 columns, joined on 5-digit county FIPS.

| File | What it is |
|---|---|
| `data/wv_county_profile.csv` | **The profile.** 55 counties, 56 columns. |
| `data/Atlas_FEMA_WV.geojson` | Atlas of Accountability core, WV subset: declarations 2011 to 2024, FEMA funding, social vulnerability, power reliability, older adults, race, heat. |
| `data/NRI_Counties_WV.geojson` | FEMA National Risk Index (December 2025), county level. |
| `data/wv_buyouts.geojson` | 2,826 buyout properties. |
| `data/wv_repetitive_loss.geojson` | 55 FEMA repetitive loss areas. |
| `data/wv_floodplain.geojson` | FEMA high-risk flood zone, statewide. |
| `data/wv_watersheds.geojson` | 33 HUC-8 watersheds. |
| `data/US_Congress_WV.geojson` | WV congressional districts. |
| `docs/DATA_DICTIONARY.md` | Every column, source, and limitation. |
| `docs/METHODOLOGY.md` | How each column was produced. |
| `tools/build_county_profile.py` | Rebuilds the profile from the layers in `data/`. |

Disaster counts and FEMA totals **reconcile exactly** to the Atlas of Accountability 2011–2024 workbook, on all 55 counties.

### Rebuilding

```bash
pip install shapely pyproj
python3 tools/build_county_profile.py
```

---

## Sources

FEMA National Risk Index · FEMA OpenFEMA (disaster declarations, Public Assistance, Hazard Mitigation, 2011–2024) · FEMA National Flood Hazard Layer and repetitive loss areas · FEMA, USACE, NRCS and HUD buyout records · USGS Watershed Boundary Dataset · CDC Social Vulnerability Index 2022 · U.S. Census Bureau ACS · U.S. Energy Information Administration

## Related

- [Atlas of Accountability](https://rebuildbydesign.github.io/atlas-of-accountability-v2/), the national interactive map
- [Atlas of Disaster](https://rebuildbydesign.org/atlas-of-disaster/)
- [`Westvirginia-atlas`](https://github.com/rebuildbydesign/Westvirginia-atlas), the WV map site (this repo is the data)
