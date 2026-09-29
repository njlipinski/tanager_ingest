# TANAGER-Ingest

Scripts for preparing reflectance spectra from the WWU TANAGER Lab for upload to the
**VISOR** spectral database (the `wwu_spec` Django project).

The lab's processed spectra live in a shared Google Drive folder as multi-sample CSV
files. Each file has one column per measurement. This repo:

1. Walks the Drive folder and skips scratch, test and calibration folders.
2. Splits each CSV into **one CSV per spectrum**. Garbage and white-reference columns
   and unwanted viewing geometries are dropped.
3. Adds a VISOR-style metadata header to each spectrum. The header holds the
   human-readable sample name, material class, locality, grain size, references,
   viewing geometry and instrument resolution.
4. Uploads the cleaned files into VISOR. This step runs separately, inside the VISOR
   Django environment.

## Repository layout

| File | Purpose |
|---|---|
| [main.py](main.py) | Entry point. Walks the Drive folder, filters folders by keyword, and calls `clean()` on every CSV. Writes to `./output/<folder name>/`. |
| [csv_cleaner.py](csv_cleaner.py) | Core logic. `clean(filepath, outputpath)` splits a TANAGER CSV into per-spectrum files and builds the metadata header. Also holds every naming-convention filter. |
| [rocks_minerals.py](rocks_minerals.py) | Two lookup sets, `minerals` and `rocks`, used to guess a sample's material class from its name or path. |
| [visor_uploader.py](visor_uploader.py) | `upload(target_dir)` ingests every CSV in each subfolder of `target_dir` into VISOR through Django ORM calls. Must run inside the `wwu_spec` environment. |
| [launch_notebook.bat](launch_notebook.bat) | Windows helper that activates the `visor` conda environment and opens a `shell_plus` Jupyter notebook in the `wwu_spec` repo. |
| [test-images/](test-images/) | Sample photos (rock slabs with a 2.8 cm reference ring). The pipeline does not use them yet. See `IMAGE_DESCRIPTION` in `csv_cleaner.py`. |
| [docs/cleaning-rules.md](docs/cleaning-rules.md) | Detailed reference: input CSV format, output format, viewing geometries, and how each metadata field is derived. |

## Requirements

- Python 3.13, the version the committed `__pycache__` was built with. Nearby versions
  should also work.
- **Cleaning step** (`main.py`): standard library only. `main.py` currently also imports
  `xlrd` and `pandas` without using them, so install those or remove the imports:
  ```
  pip install pandas xlrd
  ```
- **Upload step** (`visor_uploader.py`): a working checkout of the `wwu_spec` (VISOR)
  project and its `visor` conda environment. The script imports `django`, `recipes`
  and `visor.*` from that project and calls `django.setup()` when it loads.
- Access to the lab's shared Google Drive `processed_spectra` folder, mounted locally
  through Google Drive for Desktop.

## Usage

### 1. Clean the spectra

Edit `drive_folder` in [main.py](main.py) if your Drive mount path is different, then run:

```
python main.py
```

Output goes to `./output/<source folder name>/<spectrum id>_<column index>.csv`. The
script prints each processed file and finishes with a count. Git ignores CSVs through
`.gitignore`, so the output is never committed.

Folders are skipped when their name contains any of these words: `scratch`, `bad`,
`recon`, `test`, `training`, `troubleshoot`, `check`, `validation`, `repeatability`,
`recalibration`.

### 2. Upload to VISOR

The uploader is not wired into `main.py` yet: the call there is commented out. Run it
by hand from the VISOR environment:

1. Run `launch_notebook.bat`. Edit the hard-coded `wwu_spec` path in it first.
2. In the notebook:
   ```python
   import sys; sys.path.append(r"C:\path\to\tanager_ingest")
   from visor_uploader import upload
   upload(r"C:\path\to\tanager_ingest\output")
   ```

Files that fail validation are logged to `ingest_errors.log` in the current working
directory. The log is overwritten on every run.

## References

- Lapo, K., Hoza, K., Theuer, S., and Rice, M. S. (2024). *Reflectance spectroscopy
  datasets for the validation of TANAGER.* Geology Faculty Publications, 107.
  https://cedar.wwu.edu/geology_facpubs/107 ([DOI](https://doi.org/10.25710/qzzg-bp63))
