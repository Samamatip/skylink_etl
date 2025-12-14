from etl.extract import extract_all_data
from etl.transform import transform_data
import datetime as dt
from utilities.config import names_of_raw_data
from etl.load import load_data_to_db


def run_pipeline() -> None:
    print("Starting ETL pipeline..........................")
    start = dt.datetime.now(dt.timezone.utc) #pipeline start time in seconds
    
    try:
        # 1. Extract data
        raw_data_frames = extract_all_data(names_of_raw_data)

        # 2. Transform data
        output = transform_data(raw_data_frames.copy())

        # 3. Load data
        load_data_to_db(None, output['cleaned_data'])
    except Exception as e:
        print(f"Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
    
    print("ETL pipeline complete..........................")
    
    end = dt.datetime.now(dt.timezone.utc) #pipeline end time in seconds
    duration = (end - start).total_seconds()    #duration in seconds taken to run the pipeline
    print(f"[pipeline] Finished ETL at {end.isoformat()}Z (duration: {duration:.1f}s)")
    return None