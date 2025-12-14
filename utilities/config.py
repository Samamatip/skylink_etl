from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

names_of_raw_data = [
    "partner_roaming.xlsx",
    "raw_usage_2025_01.csv",
    "sessions.json"
]