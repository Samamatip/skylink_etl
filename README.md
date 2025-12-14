
# Skylink ETL & Dashboard

Skylink ETL is a small data engineering + analytics project that ingests partner usage data from multiple raw sources, transforms it into a clean analytical dataset, loads it into a database or files, and presents an interactive Streamlit dashboard. It includes a manual upload flow so non-technical users can drop new raw files and trigger the ETL from the UI.

**Key Features**
- End‑to‑end ETL: `extract` → `transform` → `load` orchestrated by `etl/pipeline.py`.
- Streamlit dashboard (`app.py`) to explore processed usage metrics.
- Manual upload sidebar that validates required raw files and runs ETL.
- Simple configuration utilities under `utilities/`.
- Data folder layout with `data/raw/` and `data/processed/`.

---

## Project Structure

```
app.py                      # Streamlit dashboard (manual upload + visuals)
main.py                     # CLI runner to execute the ETL pipeline
etl/
  extract.py                # Read raw sources (CSV, JSON, Excel)
  transform.py              # Clean/shape data to analysis model
  load.py                   # Persist results (e.g., CSV/DB)
  pipeline.py               # Orchestration (extract -> transform -> load)
utilities/
  config.py                 # Global paths & config helpers
  DB_connection.py          # DB connection helpers (if used)
  manual_upload.py          # Streamlit manual upload + ETL trigger
  utility.py                # Message/state helpers for UI
data/
  raw/                      # Place input files here (from Google Drive)
  processed/                # ETL outputs for analysis/visuals
requirement.txt             # Python dependencies list
lab.ipynb                   # Scratch notebook for exploration
test_db.py                  # Simple DB connectivity test (optional)
```

---

## Requirements

- Python 3.10+ (project workspace shows Python 3.13 venv; 3.10+ should work)
- Windows, macOS, or Linux
- Recommended: virtual environment (venv)

Core packages (subset; see `requirement.txt`):
- `pandas`, `numpy`, `openpyxl`
- `streamlit`, `plotly`, `altair`
- `psycopg2` (if using Postgres), `pyarrow` (optional)

---

## Sample Data

Use the sample data from this Google Drive folder:

https://drive.google.com/drive/folders/1Nngmx0HW1QVPa1QuiQjR1ehsODXxhHqN

Download the required files and place them under `data/raw/`.

Typical required files expected by the manual upload flow:
- `sessions.json`
- `raw_usage_YYYY_MM.csv` (e.g., `raw_usage_2025_01.csv`)
- `partner_roaming.xlsx`

Note: File names may be validated in `utilities/manual_upload.py`. Keep the original naming when possible.

---

## Setup

1) Create and activate a virtual environment (Windows PowerShell):
```powershell
python -m venv env
./env/Scripts/Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv env
source env/bin/activate
```

2) Install dependencies:
```bash
pip install -r requirement.txt
```

3) (Optional) Configure database connection
- If you plan to persist to a database, adjust `utilities/DB_connection.py` and any `.env` variables you use.
- If storing processed output as CSV/Parquet only, DB config can be skipped.

---

## Running the ETL

You can run the pipeline from CLI or via the Streamlit app.

CLI:
```bash
python main.py
```
This calls `etl/pipeline.py` to extract, transform, and load using the files in `data/raw/` and writes outputs to `data/processed/` (and/or a DB).

---

## Using the Streamlit App

1) Start the app:
```bash
streamlit run app.py
```

2) Manual Upload (sidebar):
- Select the required raw files (`sessions.json`, `raw_usage_YYYY_MM.csv`, `partner_roaming.xlsx`).
- Click “Process New Data” to run ETL from the UI.
- After completion, click “OK” to clear selections and notifications.

3) Explore the dashboard:
- Use filters to slice and analyze processed usage metrics.
- Visuals are built with `plotly`/`altair` on top of processed data.

Notes:
- The app manages widget state via `st.session_state`. If uploaded files appear after you click OK, ensure you’re on the latest `main`; this behavior is addressed in `utilities/manual_upload.py` using a rotating uploader key.

---

## Configuration

- Paths and constants: `utilities/config.py`
- DB connection: `utilities/DB_connection.py`
- UI messaging/state helpers: `utilities/utility.py`
- Manual upload + ETL trigger: `utilities/manual_upload.py`

If you use environment variables, create a `.env` at the project root and load with `python-dotenv`.

---

## Developer Tips

- Data folders:
  - Drop raw inputs into `data/raw/`.
  - ETL writes outputs to `data/processed/`.
- If you change the schema or file naming, update both `etl/extract.py` and `utilities/manual_upload.py` to keep validations consistent.
- For Windows line endings warnings (CRLF/LF), set Git config as desired:
```bash
# Convert CRLF on checkout/commit (Windows-friendly)
git config core.autocrlf true
# Or prefer LF in repo, convert on commit only
git config core.autocrlf input
```

---

## Troubleshooting

- “non-fast-forward” on `git push`:
  - Run `git pull --rebase origin main` and retry `git push -u origin main`.
- Streamlit shows stale uploads after OK:
  - Ensure latest code is pulled; uploader widget is reset via session key bump.
- Missing dependencies:
  - Re-check `requirement.txt` and reinstall; verify your venv is active.

---

## License

This project is intended for educational and internal use. No explicit license is set.
# skylink_etl

last updated by https://github.com/Samamatip
@Olusola Samson