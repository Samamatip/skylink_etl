import streamlit as st
import os
from etl.pipeline import run_pipeline
from utilities.utility import set_message, clear_messages
from utilities.config import RAW_DATA_DIR


def handle_manual_upload() -> None:
    # Initialize session state keys
    if 'etl_completed' not in st.session_state:
        st.session_state['etl_completed'] = False
    if 'uploaded_raw_paths' not in st.session_state:
        st.session_state['uploaded_raw_paths'] = []
    if 'upload_key' not in st.session_state:
        st.session_state['upload_key'] = 0
        
    uploaded_files = None
    #Input for raw data upload
    uploaded_files = st.sidebar.file_uploader(
        "Upload Raw Data Files",
        type=["csv", "xlsx", "xls", "json"],
        accept_multiple_files=True,
        key=f"raw_uploader_{st.session_state['upload_key']}"
    )
    files_list = list(uploaded_files) if uploaded_files else None
    
    if files_list is not None:
        uploaded_names = [f.name for f in files_list]
        required_files = {'sessions.json','raw_usage_2025_01.csv','partner_roaming.xlsx'}
    
        for fname in uploaded_names:
            if fname not in required_files:
                set_message(
                    "warn",
                    f"Unexpected file '{fname}' uploaded. Please upload only the required files."
                )
                return  # Exit the function on invalid file upload
    
        if not required_files.issubset(set(uploaded_names)):
            set_message(
                "warn", 
                "Please upload all three required files: sessions.json, raw_usage_2025_01.csv, partner_roaming.xlsx"
            )
        elif (required_files.issubset(set(uploaded_names))):
            set_message(
                "success",
                "All required files uploaded successfully!"
            )

            # ETL Pipeline Trigger button
            if st.sidebar.button("Process New Data (Run ETL Pipeline)", help="Click to run the ETL pipeline and update the database with newly uploaded data."):
                with st.spinner("Processing files and running ETL pipeline..."):
                    try:
                        clear_messages()
                        # Save uploaded files to raw data directory
                        progress_bar = st.progress(0)
                        set_message(
                            "info", 
                            "Uploading files..."
                        )

                        # Ensure raw directory exists
                        os.makedirs(RAW_DATA_DIR, exist_ok=True)

                        saved_paths = []
                        for idx, uploaded_file in enumerate(uploaded_files):
                            file_path = os.path.join(RAW_DATA_DIR, uploaded_file.name)
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            saved_paths.append(file_path)
                            progress_bar.progress((idx + 1) / (len(uploaded_files) + 1))

                        # Persist saved raw file paths for later cleanup
                        st.session_state['uploaded_raw_paths'] = saved_paths

                        set_message(
                            "info", 
                            "Files uploaded successfully. Running ETL pipeline..."
                        )

                        # Call run_pipeline directly, to process the newly uploaded files
                        run_pipeline()
                        
                        progress_bar.progress(1.0)
                        set_message(
                            "success",
                            "✅ ETL Pipeline completed successfully!"
                        )

                        # Clear cache so dashboard refreshes with new data
                        st.info("📊 Dashboard data refreshed. Scroll down to see updated analytics.")
                        
                        # Mark pipeline completion in session state so we show cleanup button
                        st.session_state['etl_completed'] = True
                        st.session_state['uploaded_raw_paths'] = saved_paths
                        
                    except Exception as e:
                        set_message(
                            "error",
                            f"❌ Error during ETL pipeline: {str(e)}"
                        )
                        
                        
def cleanup_uploaded_files() -> None:
    """Cleanup uploaded raw files after ETL completion."""
    if st.session_state.get('etl_completed', False):
        raw_paths = st.session_state.get('uploaded_raw_paths', [])
        for path in raw_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                set_message(
                    "warn",
                    f"Could not delete file {path}: {str(e)}"
                )
        # Reset session state
        st.session_state['etl_completed'] = False
        st.session_state['uploaded_raw_paths'] = []
        # Bump uploader key so the widget re-initializes and clears selection
        st.session_state['upload_key'] = st.session_state.get('upload_key', 0) + 1
        clear_messages()
    return None