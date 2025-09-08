import os
import hashlib
import polars as pl
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.core.api.simm import update_simm_date_from_df

from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str

from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_HIST_NAME_DEFAULT, SIMM_CUTOFF_DATE, SIMM_COLUMNS, SIMM_RENAME_COLUMNS


SCHEMA_OVERRIDES = {v["name"] : v["type"] for v in SIMM_COLUMNS.values()}

SCHEMA_OVERRIDES_WTH_DATE = SCHEMA_OVERRIDES.copy()
SCHEMA_OVERRIDES_WTH_DATE["Date"] = pl.Date


def read_simm_history_from_excel (
        
        fund : Optional[str] = None, # FUND_HV
        simm_fund_paths : Optional[Dict] = None, # SIMM_FUNDS_DIR_PATHS,
        specific_cols : Optional[List] = None,
        schema_overrides : Optional[Dict] = None, # SCHEMA_OVERRIDES
        cutoff_date : Optional[str] = None # SIMM_CUTOFF_DATE

    ) -> Optional[pl.DataFrame] :
    """
    Read historical SIMM data for a given fund from a local Excel file.

    This function resolves the absolute path to the fund's SIMM Excel file, and uses
    Polars to read and optionally filter or cast the columns using a provided schema.

    Args:
        fund (str): Fund identifier used to determine the folder path (e.g. "HV").
        simm_fund_paths (dict): Dictionary mapping fund names to their folder paths.
        excel_relative_filename (str): The relative filename of the SIMM Excel file.
        specific_cols (list, optional): List of column names to retain after reading.
        schema_overrides (dict, optional): Dictionary mapping column names to Polars dtypes
                                           to enforce casting during import.

    Returns:
        simm_history_df (pl.DataFrame | None) : A Polars DataFrame containing the SIMM history,
                             or None if the fund path could not be resolved.
    """
    # Checks for the fundation path
    
    schema_overrides = SCHEMA_OVERRIDES_WTH_DATE if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys()) if specific_cols is None else specific_cols
    cutoff_date = SIMM_CUTOFF_DATE if cutoff_date is None else cutoff_date

    excel_file_abs_pth = get_simm_abs_path_by_fund(fund, simm_fund_paths)

    if excel_file_abs_pth is None :

        log(f"[-] {excel_file_abs_pth} does not exist or not found.")
        return None, None
    
    try :

        simm_history_df, _ = load_excel_to_dataframe(excel_file_abs_pth, specific_cols=specific_cols, schema_overrides=schema_overrides)

        if simm_history_df is None :
            
            log("[-] No data returned from the SIMM file", "error")
            return None, None

    except Exception as e :

        log(f"[-] Error getting the SIMM data : {e}", "error")
        return None, None

    
    try :

        cutoff_date_parsed = dt.datetime.strptime(cutoff_date, "%Y-%m-%d").date()
        
        if "Date" in simm_history_df.columns :

            simm_history_df = simm_history_df.filter(pl.col("Date") >= pl.lit(cutoff_date_parsed))
            md5_hash = hashlib.md5(simm_history_df.write_parquet()).hexdigest()

        else :
            
            log(f"[!] 'Date' column not found in DataFrame. Cannot apply cutoff.", "warning")
    
    except Exception as e :

        return None, None

    return simm_history_df, md5_hash


def write_simm_history_from_df (
        
        fund : Optional[str] = None,
        simm_fund_paths : Optional[Dict] = None, # SIMM_FUNDS_DIR_PATHS,
        specific_cols : Optional[List] = None,
        schema_overrides : Optional[Dict] = None, # SCHEMA_OVERRIDES

    ) -> None :
    """
    
    
    """
    schema_overrides = SCHEMA_OVERRIDES_WTH_DATE if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys()) if specific_cols is None else specific_cols

    file_abs_path = get_simm_abs_path_by_fund(fund, simm_fund_paths)


    return None


def is_simm_history_updated_from_df (

        _df : pl.DataFrame,
        md5hash : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        specific_col : str = "Date",
    
    ) -> bool :
    """
    Filters and updates the SIMM history if today's data is missing.

    This function is cached using Streamlit's st.cache_data,
    and will re-run only if the input DataFrame changes.

    Args:
        df (pl.DataFrame): SIMM history dataframe (with column 'Date').
        specific_col (str): Name of the date column.
        cutoff_date (str): Minimum allowed date (entries before will be removed).

    Returns:
        pl.DataFrame: Updated and filtered SIMM history.
    """
    if _df is None :

        log("[-] The dataframe is NULL. Impossible to get information.","error")
        return None
        
    date_str = date_to_str(date)
    lastest_date = _df.select(specific_col).to_series()[-1] # This line is exclusevely for today's date. Not general purpose

    if lastest_date == date_str :
        
        log("[*] Dataframe and SIMM excel already updated with today's date !", "info")
        return True

    # Case where the lastest day is not in the Dataframe (so into the excel file) -> Need to call the API (not in this file)
    return False


def is_simm_history_updated_from_file (
        
        fund : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        specific_col : str = "Date"

    ) -> bool :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    date = date_to_str(date)

    df_simm, md5_hash = read_simm_history_from_excel(fund)
    updated = is_simm_history_updated_from_df(df_simm, md5_hash, date, specific_col)

    return updated


def get_updated_all_simm_history (
    
        fund : Optional[str] = None,
        simm_fund_paths : Optional[Dict] = None,
        specific_cols : Optional[List] = None,
        schema_overrides : Optional[Dict] = None,
        type = int
    
    ) -> Optional[pl.DataFrame] :
    """
    Function to get all leverages from the leverage folder and save them in a single file.
    """
    specific_cols = list(SCHEMA_OVERRIDES_WTH_DATE.keys())
    schema_overrides = SCHEMA_OVERRIDES if schema_overrides is None else schema_overrides

    simm_history_df, md5_hash = read_simm_history_from_excel(fund, simm_fund_paths, specific_cols, schema_overrides)
    updated = is_simm_history_updated_from_df(simm_history_df, md5_hash)

    if updated :
        return simm_history_df, md5_hash

    simm_history_df, md5_hash = update_simm_date_from_df(simm_history_df, md5_hash, fund)

    return simm_history_df


def get_simm_abs_path_by_fund (
        
        fund : Optional[str] = None,
        simm_fund_paths : Optional[Dict] = None, # SIMM_FUNDS_DIR_PATHS,
        basename_file : Optional[str] = None

    ) -> Optional[str] :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    simm_fund_paths = SIMM_FUNDS_DIR_PATHS if simm_fund_paths is None else simm_fund_paths
    basename_file = SIMM_HIST_NAME_DEFAULT if basename_file is None else basename_file

    file_abs_directory = simm_fund_paths.get(fund)

    file_abs_path = os.path.join(file_abs_directory, basename_file)

    return file_abs_path

