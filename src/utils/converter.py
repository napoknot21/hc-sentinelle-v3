import polars as pl
import time

from src.config.parameters import *
from src.utils.logger import *

def convert_excel_to_dataframe (excel_file_abs_pth : str, sheet_name : str, specific_cols : list, schema_overrides : dict) -> pl.DataFrame :
    """
    Loads an Excel file and returns it as a Polars dataframe, applying schema overrides.

    Args:
        file_abs_pth (str): Absolute path to the Excel file.
        sheet_name (str): Sheet name to read from.
        specific_cols (list): List of columns to import. If None, then all columns
        schema_overrides (dict): Dictionary mapping column names to Polars types.

    Returns:
        df (pl.DataFrame | None) : Loaded dataframe, or None if an error occurs.
    """
    if not check_file_exists(excel_file_abs_pth) :
        
        log(f"\n[-] File not found : {excel_file_abs_pth}\n", "error")
        return None

    try :

        # sving the time of execution
        start = time.time()
        
        if sheet_name is None or sheet_name == "" :
        
            sheet_index = 0

        df = pl.read_excel(
            source=excel_file_abs_pth,
            sheet_name=sheet_name,
            columns=specific_cols,              # If None, pl manage this case
            schema_overrides=schema_overrides   # If None, Polars manages this case
        )
        
        log(f"[*] [POLARS] Lecture in {time.time() - start:.2f} seconds of {excel_file_abs_pth}", "info")

        return df
    
    except Exception as e :

        log(f"\n[-] Error while converting the Excel file : {e}\n", "error")
        return None


def check_file_exists (file_abs_pth : str) :
    """
    Checks if a file exists on disk.

    Args:
        file_abs_pth (str): Full path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    import os
    return os.path.isfile(file_abs_pth)













def check_if_exists (filename) :
    """
    This private function checks if the file exists
    """
    return os.path.isfile(filename)
