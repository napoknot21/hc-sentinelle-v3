import hashlib
import polars as pl
import datetime as dt
import streamlit as st


from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe
from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_HIST_NAME, SIMM_CUTOFF_DATE, SIMM_COLUMNS


RENAME_COLUMNS = {k : v["name"] for k, v in SIMM_COLUMNS.items()}
SCHEMA_OVERRIDES = {v["name"] : v["type"] for v in SIMM_COLUMNS.values()}

SCHEMA_OVERRIDES_WTH_DATE = SCHEMA_OVERRIDES.copy()
SCHEMA_OVERRIDES_WTH_DATE["Date"] = pl.Utf8


def read_simm_history_from_excel (
        
        fund : str = FUND_HV,
        simm_fund_paths : dict = SIMM_FUNDS_DIR_PATHS,
        specific_cols : list = None,
        schema_overrides : dict = SCHEMA_OVERRIDES

    ) -> pl.DataFrame | None :
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
    excel_file_abs_pth = simm_fund_paths.get(fund)

    if excel_file_abs_pth is None :

        log(f"[-] {excel_file_abs_pth} does not exist or not found.")
        return None

    simm_history_df = load_excel_to_dataframe(excel_file_abs_pth, specific_cols=specific_cols, schema_overrides=schema_overrides)
    df_hash = hashlib.md5(simm_history_df.write_csv().encode()).hexdigest()

    return simm_history_df, df_hash


@st.cache_resource()
def update_simm_history_from_df (

        _df : pl.DataFrame,
        md5hash : str = None,
        date : dt.datetime = None,
        specific_col : str = "Date",
        cutoff_date : str = SIMM_CUTOFF_DATE
    
    ) -> pl.DataFrame :
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
        
    date_to_str = date.strftime("%Y-%m-%d")
    lastest_date = _df.select(specific_col).to_series()[-1] # This line is exclusevely for today's date. Not general purpose

    if lastest_date == date_to_str :
        
        log("[*] Dataframe and SIMM excel already updated with today's date !", "info")
        return _df

    # Case where the lastest day is not in the Dataframe (so into the excel file)


    return None



def find_all_simm_history (
    
        fund : str = FUND_HV,
        simm_fund_paths : dict = SIMM_FUNDS_DIR_PATHS,
        specific_cols : list = list(SCHEMA_OVERRIDES_WTH_DATE.keys()),
        schema_overrides : dict = SCHEMA_OVERRIDES,
        type = int
    
    ) :
    """
    Function to get all leverages from the leverage folder and save them in a single file.
    """
    simm_history_df, md5_hash = read_simm_history_from_excel(fund, simm_fund_paths, specific_cols, schema_overrides)

    updated = update_simm_history_from_df(simm_fund_paths, md5_hash, simm_fund_paths, specific_cols, schema_overrides)

    

    return simm_history_df
