from pathlib import Path
from utilities.config import RAW_DATA_DIR
from utilities.utility import read_df

def extract_all_data(file_paths): # Note: file_paths is a list of file paths and only csv, json, and excel files are supported
    print("Initiating data extraction..........................")
    if not file_paths or len(file_paths) == 0:
        raise ValueError("The list of file paths is empty.")
    data_frames = {}
    print("Extracting data from files..........................")
    for path in file_paths:
        df = read_df(f"{RAW_DATA_DIR}/{path}")
        df_key = Path(path).stem.split('/')[-1]  # Use the file name without extension
        # get the key word roaming, usage, sessions as the key for the file that contains the word and assign it as the key.
        df_key = 'roaming' if 'roaming' in df_key else 'usage' if 'usage' in df_key else 'sessions' if 'sessions' in df_key else df_key
        data_frames[df_key] = df
        print(f"Extracted {df_key} data with {len(df)} records.")
    print("Data extraction complete..........................")
    return data_frames

