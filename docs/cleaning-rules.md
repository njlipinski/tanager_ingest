# Cleaning rules

A reference for what `csv_cleaner.clean()` expects as input, what it writes, and how it
decides each metadata field. Everything described here lives in
[csv_cleaner.py](../csv_cleaner.py).

## Input CSV format

The cleaner reads the file as plain comma-split text, not with the `csv` module, so
quoted commas are not supported. It expects this layout:

| Row | Column A | Columns B… |
|---|---|---|
| 1 | (ignored) | (ignored) |
| 2 | (ignored) | **Sample name** for each spectrum. This becomes the VISOR *Spectrum ID*. |
| 3 | (ignored) | **Viewing geometry**, e.g. `i=12 e=35 az=0` |
| … | … | … |
| *n* | `Wavelength` | Column header for the data |
| *n*+1… | wavelength (nm) | reflectance values |

The data block starts at the first row whose column A is exactly `wavelength`
(case-insensitive).

## Output format

`clean()` writes one file per kept column, named `<sample name>_<column index>.csv`.
Each file is a two-column CSV: a metadata header, followed by the wavelength block copied
from the input.

```
Other Information,Probe Type: standard probe; Filename: <full input path>
Sample Name,Dry Falls Basalt
Material class,Rock
Locality,Columbia River Flood Basalts
Grain Size,Whole Object
References,<url>
Database of origin:,WWU TANAGER Lab
Spectrum ID,df_18_002_a_std
Original Sample ID,df_18_002_a
Viewing geometry,i30 e0 az0
Resolution,3 nm @ 700 nm (VNIR 350-1000 nm); 8 nm @ 1400 nm (SWIR1 1000-1800 nm); 8 nm @ 2100 nm (SWIR2 1800-2500 nm)
Wavelength,<original column header>
350,0.0812
...
```

Empty fields are left out entirely, because VISOR rejects NaN values. See `add_row()`.

## Columns that get dropped

A column is skipped when either of these is true:

1. Its sample name contains a `SKIP_WORDS` substring: `gar` (catches the misspellings
   of "garbage"), `white reference`, `bad`, `test`, `_gr10`.
2. Its viewing geometry is not in `VIEWING_GEOMETRIES`, or it conflicts with the
   geometry already chosen for its category (see below).

## Viewing geometries

The `=` signs are stripped from the geometry string (`i=12 e=35 az=0` → `i12 e35 az0`).
The result is then matched against these categories:

| Category | Geometries | Spectrum ID suffix | Probe type |
|---|---|---|---|
| `small_diameter_probe` | `i0 e0 az0` | none | small diameter probe |
| `standard_probe` | `i12 e35 az0` | none | standard probe |
| `std_geo` | i30/35 e0, i0 e30/35 | `_std` | TANAGER |
| `fwd_geo` | ±i30 ∓e45/50, ±i45/50 ∓e30 | `_fwd` | TANAGER |
| `spec_geo` | ±i30 ∓e30, ±i45 ∓e45 | `_spec` | TANAGER |
| `back_geo` | ±i30 ±e45/50, ±i45/50 ±e30 | `_back` | TANAGER |
| `v_fwd_geo` | ±i45/50 ∓e60, ±i60 ∓e45/50, ±i70 ∓e58 | `_v.fwd` | TANAGER |

Each category keeps **one geometry per input file**. The first geometry seen in a
category is locked in, and later columns in that category with a different geometry are
skipped. Columns with the same geometry are all kept.

## How the metadata is derived

`apply_filters()` runs every filter below. The **first one that matches**, in this
order, supplies Sample Name and Material class, plus any other fields it returns:

| # | Filter | Matches when | Supplies |
|---|---|---|---|
| 1 | `hardcoded_values` | The sample name is one of a few specific one-offs (XRD holders, `gypsum_125`, `powdered_hematite`) | name, class |
| 2 | `get_alivia_info` | The path contains an Alivia, Max clay/sulfate, Max goniometer, Max mixture or Kristiana mafic-mixture dataset name, and the sample is not in `alivia_exceptions` | name expanded from `<pct><abbrev>` parts (e.g. `50mon_50sap` → `montmorillonite 50%, saponite 50%`), class = Mixture |
| 3 | `get_max_info` | The path is one of Max's LPSC pre-coat or post-coat slab files, and the sample name is an Expanse codename (`farragut`, `pella`, …) | name, class = Rock, locality = Twin Sisters Mountains, **renamed Spectrum ID** `TS-20-08-<code>-pre/post` |
| 4 | `get_header_info` | The sample name contains a site acronym followed by `_`, `-` or space: `TS`, `TM`, `APA`, `DF`, `FC`, `GR`, `SM`, `KD`/`KDT`, `PC`/`PCT`, `MIT`, `CRB` | name, class = Rock, locality, grain size = Whole Object |
| 5 | `get_sample_type_mods` | The path or sample name contains `mix`, `lunar_simulant`, a reference-target name, a reference color in a witness or validation folder, or any entry in `rocks_minerals` | class only (Mixture / Rock / Reference / Mineral) |

The **References** field is filled separately, from the file path by
`get_reference_info()`: `sammy` → Sammy's thesis, `max` → Max's LPSC 2024 abstract,
`alivia` → Alivia's JGR Planets paper.

The **Spectrum ID** is the sample name (or the renamed ID from filter 3) plus the
geometry suffix. The **Original Sample ID** is the same value without the suffix.

## Constants that are defined but not used yet

- `REF_CEDAR`, `REF_CEDAR_DOI`: the dataset citation.
- `RESOLUTION_SHORT`: a shorter form of `RESOLUTION`.
- `IMAGE_DESCRIPTION`: meant for attaching sample photos, like those in `test-images/`.
