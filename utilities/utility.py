import pandas as pd

def read_df(data_path: str) -> pd.DataFrame:
    """
        Reads a given file from the given path,
        Determine the data type from the name,
        returns a pandas DataFrame.
    """
    try:
        if data_path.endswith('.csv'):
            return pd.read_csv(data_path)
        elif data_path.endswith('.xlsx') or data_path.endswith('.xls'):
            return pd.read_excel(data_path)
        elif data_path.endswith('.json'):
            return pd.read_json(data_path, lines=True)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV, Excel, or JSON file.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    
    
# function to execute SQL queries using a given psycopg2 connection
def execute_query(connection, query):
    if connection:
        cur = connection.cursor()
    else:
        cur = None
    if cur:
        try:
            cur.execute(query)
            connection.commit()
            print("Query executed successfully")
        except Exception as e:
            print(f"Error executing query: {e}")
            connection.rollback()
        finally:
            cur.close()
    else:
        print("No database connection available")
        

# function to execute many SQL queries with parameters using a given psycopg2 connection
def execute_many_query(connection, query, data):
    if connection:
        cur = connection.cursor()
    else:
        cur = None
    if cur:
        try:
            cur.executemany(query, data)
            connection.commit()
            print("Queries executed successfully")
        except Exception as e:
            print(f"Error executing queries: {e}")
            connection.rollback()
        finally:
            cur.close()
    else:
        print("No database connection available")
        
        
#  function to show status updates
message = {
    "warn": "",
    "info": "",
    "error": "",
    "success": ""
}

def clear_messages() -> None:
    """Clear all messages."""
    global message
    for key in message:
        message[key] = ""

def set_message(type:str, new_message: str) -> dict:
    """Update the global message object."""
    global message
    
    clear_messages()  # Clear existing messages before setting a new one
    if type in message:
        message[type] = new_message
    else:
        message["info"] = new_message
    return message

def get_message(msg_type: str = None) -> dict | str:
    """Retrieve the current message(s)."""
    if msg_type:
        return message.get(msg_type, "")  # Get specific type
    return message  # Get all messages