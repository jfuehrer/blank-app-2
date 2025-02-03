# this module include common utilities like csv handling (load_data, validate_csv_columns)and simliar functions to avoid code reptition
import pandas as pd
def load_and_validate_csv(file_path, required_columns):
    data = pd.read_csv(file_path)
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    return data