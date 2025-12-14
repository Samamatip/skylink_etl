
import traceback

def insert_data_to_db_sqlalchemy(engine, cleaned_data):
    print("Starting data loading into the database using SQLAlchemy..........................")

    if engine is None:
        print("Error: Engine is None")
        return None

    usage_df = cleaned_data.get('usage') if cleaned_data else None
    if usage_df is None:
        print("Error: No 'usage' dataframe found in cleaned_data")
        return None

    if usage_df.empty:
        print("No usage data to load; skipping")
        return None

    # Drop duplicates prior to insert so we do not hit unique violations on reruns
    usage_df = usage_df.drop_duplicates(subset=['msisdn', 'session_id', 'timestamp'])

    try:
        # Use engine's connection context manager for proper transaction handling
        with engine.begin() as conn:
            # Insert data into USAGE table (append preserves existing data)
            rows_inserted = usage_df.to_sql('USAGE', conn, if_exists='append', index=False)
            print(f"Data inserted successfully: {rows_inserted} rows")

            # Remove any existing duplicates in the table to allow unique index creation
            conn.exec_driver_sql(
                """
                WITH ranked AS (
                    SELECT ctid, ROW_NUMBER() OVER (
                        PARTITION BY msisdn, session_id, "timestamp"
                        ORDER BY ctid
                    ) AS rn
                    FROM "USAGE"
                )
                DELETE FROM "USAGE" u
                USING ranked r
                WHERE u.ctid = r.ctid AND r.rn > 1;
                """
            )
            print("Removed duplicate rows in table before enforcing uniqueness")

            # Enforce uniqueness on the key columns to prevent duplicates on reruns
            conn.exec_driver_sql(
                'CREATE UNIQUE INDEX IF NOT EXISTS idx_usage_msisdn_session_ts '
                'ON "USAGE" (msisdn, session_id, "timestamp")'
            )
            print("Unique index ensured on (msisdn, session_id, timestamp)")
            print("Transaction committed automatically")

    except Exception as e:
        print(f"Error inserting data: {e}")
        traceback.print_exc() # Print the full traceback for debugging
    finally:
        # Dispose of the engine connection pool
        if engine:
            engine.dispose()
            print("SQLAlchemy engine disposed")

    print("Data loading complete..........................")
    return None

def load_data_to_db(connection, cleaned_data):
    print("Starting data loading into the database..........................")
    
    # Import here to avoid circular imports
    from utilities.DB_connection import make_sqlalchemy_db_connection
    
    # Create SQLAlchemy engine for data loading
    sqlalchemy_engine = make_sqlalchemy_db_connection()
    
    if sqlalchemy_engine is None:
        print("Error: Could not create database engine")
        return None
    
    # Insert data into USAGE table using SQLAlchemy
    print("\nInserting data into table...")
    insert_data_to_db_sqlalchemy(sqlalchemy_engine, cleaned_data)
    
    print("Data loading complete..........................")
    return None