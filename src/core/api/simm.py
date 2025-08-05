import os
import polars as pl
import datetime as dt
import streamlit as st

from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_HIST_NAME
from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.core.api.client import get_ice_calculator

from src.utils.data_io import load_excel_to_dataframe
from src.utils.logger import log


SIMM_COLUMNS = {

    "group" : { "name" : "Counterparty", "type": pl.Utf8 },

    "postIm" : { "name" : "IM", "type" : pl.Float64 },

    "post.price" : { "name" : "MV", "type" : pl.Float64 },
    "post.priceCapped" : { 'name' : 'MV Capped', 'type' : pl.Float64 },
    "post.priceCappedMode" : { "name" : "MV Capped Type", "type" : pl.Utf8 },
    'post.shortfall' : { "name" : "Available / Shortfall Amount", "type" : pl.Float64 },
    "post.clientMarginRatio" : { "name" : "Client Margin Rate", "type" : pl.Float64 },

}

RENAME_COLUMNS = {k : v["name"] for k, v in SIMM_COLUMNS.items()}

SCHEMA_OVERRIDES = {v["name"] : v["type"] for v in SIMM_COLUMNS.values()}


def fetch_raw_simm_data (date : dt.datetime = dt.datetime.now(), fund : str = FUND_HV, fund_map : dict = FUND_NAME_MAP) -> pl.DataFrame | None :
    """
    Fetch raw bilateral SIMM data from ICE API and normalize the JSON response.

    Args:
        date (datetime): The date for which to retrieve SIMM data.
        fund (str): Fund identifier used in the API call.

    Returns:
        normal_json (pl.DataFrame | None) : A normalized Polars DataFrame containing the SIMM data,
                             or None if the API call or normalization fails.

    Note:
        This function refers to the "get_simm()" precedent version.
    """
    try :

        ice_calc = get_ice_calculator()
        fund_name = fund_map[fund]

        if not fund_name :

            log(f"[-] Fund '{fund}' not found in FUND_NAME_MAP", "error")
            return None

        log("[+] Successfully connected to the API ICE and Fundation name found", "info")

    except Exception as e :

        log(f"[-] Error during connexion to the API ICE: {e}", "error")
        
        return None

    # Billateral Data request
    bilateral_im = ice_calc.get_billateral_im_ctpy(date, fund=fund_name)
    
    if bilateral_im is None :
        
        log("[-] Error during bilateral IM data request", "error")
        return None

    log("[+] Bilateral IM data request successful")

    try :

        # Dictionarry billateral IM normalization
        normal_json = pl.json_normalize(bilateral_im)

        if normal_json is None :

            log("[-] Error during bilateral IM data normalization", "error")
            return None

        log("[+] Bilateral IM data normalization successful")

        return normal_json
    
    except Exception as e :

        log(f"[-] Error during bilateral IM data normalization: {e}", "error")
        return None


def load_simm_data (
        
        date : dt.datetime = dt.datetime.now(),
        fund : str = FUND_HV,
        rename_cols : dict = RENAME_COLUMNS,
        specific_cols : list = list(RENAME_COLUMNS.values())

    ) -> pl.DataFrame | None :
    """
    Load and preprocess SIMM data from the ICE API.

    This function wraps `fetch_raw_simm_data`, renames its columns, and filters them to keep only relevant ones.

    Args:
        date (datetime): The date for which to load SIMM data.
        fund (str): Fund identifier.
        rename_cols (dict): Mapping of raw API column names to desired standardized column names.
        specific_cols (list): List of final column names to retain in the resulting DataFrame.

    Returns:
        pl.DataFrame | None: Cleaned Polars DataFrame with renamed and filtered columns,
                             or None if the fetch fails.
    """
    # Fetch and get the SIMM
    try :

        data = fetch_raw_simm_data(date, fund)

    except Exception as e :

        log("[-] Error getting the SIMM data...", "error")
        return None
    
    log("[+] SIMM data successfully got", "info")
    
    # Data handling (Rename columns)
    data_rename = data.rename(rename_cols)

    # Polars normally manages the "," (commas) by itself
    data_cols = data_rename[specific_cols]

    print(data_cols)

    return data_cols


def read_simm_history_from_excel (
        
        fund : str = FUND_HV,
        simm_fund_paths : dict = SIMM_FUNDS_DIR_PATHS,
        excel_relative_filename : str = SIMM_HIST_NAME,
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
    fundation_path = simm_fund_paths.get(fund)

    # Get the /path/to/the/file.extension
    excel_file_abs_pth = os.path.join(fundation_path, excel_relative_filename)

    simm_history_df = load_excel_to_dataframe(excel_file_abs_pth, specific_cols=specific_cols, schema_overrides=schema_overrides)

    return simm_history_df


def find_all_simm_history (fund : str = FUND_HV, relative_filename : str = SIMM_HIST_NAME, type = int) :
    """
    Function to get all leverages from the leverage folder and save them in a single file.
    """
    fundation_path = SIMM_FUNDS_DIR_PATHS[fund] # Check for the fundation path
    excel_file_abs_pth = os.path.join(fundation_path, relative_filename) # Get the /path/to/the/file.extension

    simm_history_df = load_excel_to_dataframe(excel_file_abs_pth)

    # TO DO

    return simm_history_df



# results_2 = read_simm_history_from_excel(FUND_HV)
#print(results_2)
