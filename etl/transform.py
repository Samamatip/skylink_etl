import pandas as pd

def _clean_dfs(dfs):
    cleaned = {}
    for key, df in dfs.items():
        if df.empty:
            cleaned[key] = df
            continue  # Skip empty DataFrames
        
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_", regex=False) #format the columns
        
        if 'avg_throughput' in df.columns:
            median_throughput = df['avg_throughput'].median()   #calculate median of avg_throughput
            df['avg_throughput'] = df['avg_throughput'].fillna(median_throughput)
            
        if 'session_id' in df.columns:    
            df = df.drop_duplicates(subset=['session_id'], keep='first') 
        
        if 'download_mb' in df.columns and 'upload_mb' in df.columns:
            df['total_usage_mb'] = df['download_mb'].fillna(0) + df['upload_mb'].fillna(0)

        # drop -ve values for duration_ms
        if 'duration_ms' in df.columns:
            df = df[df['duration_ms'] >= 0]
            
        #parse date columns to datetime format if any
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        #replace missing values in 'app_category' with 'unknown'
        if 'app_category' in df.columns:
            df['app_category'] = df['app_category'].fillna('unknown')
        
        cleaned[key] = df
            
    return cleaned


# Function to aggregate daily usage per msisdn
def _aggregate_daily_usage(df: pd.DataFrame) -> pd.DataFrame:
    
    if df.empty or 'msisdn' not in df.columns or 'timestamp' not in df.columns:
        return pd.DataFrame()  # Return empty DataFrame if its invalid
    #GroupBy
    df['date'] = df['timestamp'].dt.date
    #1. Aggregate total usage, number of sessions, average throughput per msisdn per day
    aggregations = {
        "total_usage_mb": ("total_usage_mb", "sum"),
        "sessions": ("session_id", "nunique"),
        "avg_throughput": ("avg_throughput", "mean")
    }
    
    # 2. conditionally add the latency/count aggregation
    if 'latency_ms' in df.columns:
        aggregations["latency_ms"] = ("latency_ms", "mean")
    else:
        aggregations["latency_ms"] = ("timestamp", "count")  # Placeholder aggregation if latency_ms doesn't exist
        
    # 3. Apply the constructed dictionary to .aggregate()
    agg = (
        df.groupby(['msisdn', 'date']).agg(**aggregations)
        .reset_index()
    )
    return agg

def transform_data(dfs):
    print("Transforming data..........................")
    cleaned_dfs = _clean_dfs(dfs)
    daily_usage_agg = pd.DataFrame()
    if 'usage' in cleaned_dfs:
        daily_usage_agg = _aggregate_daily_usage(cleaned_dfs['usage'])
    print("Data transformation complete............")
    return {
        'cleaned_data': cleaned_dfs,
        'daily_usage_aggregation': daily_usage_agg
    }