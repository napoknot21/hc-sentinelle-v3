from __future__ import annotations

import os
import time
import hashlib
import polars as pl
import datetime as dt
import streamlit as st

from typing import Optional, Dict, List, Tuple

from src.core.api.client import get_ice_calculator

from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_RENAME_COLUMNS

from src.utils.formatters import date_to_str
from src.utils.logger import log


@st.cache_data(ttl=60000, show_spinner=False)
def fetch_raw_simm_data (
    
        fund : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
    
    ) -> Optional[Tuple[pl.DataFrame, str]] :
    """
    Fetch raw bilateral SIMM (ICE) and return (df, md5) or None.

    Args:
        date (str | datetime | date): The date for which to retrieve SIMM data.
        fund (str): Fund identifier used in the API call.

    Returns:
        normal_json (pl.DataFrame | None) : A normalized Polars DataFrame containing the SIMM data, or None if the API call or normalization fails.
        md5 (str | None) : MD5 hash for the normal_json content, in order to get a local cache

    Note :
        This function refers to the "get_simm()" precedent version.
    """
    #time = time.time()

    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund

    fund_map = FUND_NAME_MAP # We need to hardcode this value in order to get cache parameters of this function
    fund_name = fund_map.get(fund) # We get the fundation in initials (HV, etc)

    if not fund_name :

        log(f"[-] Fund '{fund}' not found in FUND_NAME_MAP", "error")
        return None, None
    
    # Ice API connexion
    try :

        calculator = get_ice_calculator()
        log(f"[+] ICE API client ready | fund={fund_name} | date={date}", "info")

    except Exception as e :

        log(f"[-] ICE API initialization failed: {e}", "error")
        return None, None
    
    # Network bound
    try :

        bilateral_im = calculator.get_bilateral_im_ctpy(date, fund_name)
        
        if bilateral_im is None :
        
            log(f"[-] Error during bilateral IM data request | fund={fund_name} | date={date}", "error")
            return None, None

    except Exception as e :

        log(f"[-] Error during bilateral IM request: {e}", "error")
        return None, None

    log("[+] Bilateral IM data request successful")
    try :

        # Dictionarry billateral IM normalization
        normal_json = pl.json_normalize(bilateral_im)

        if normal_json is None :

            log("[-] Error during bilateral IM data normalization", "error")
            return None, None
        
        md5_hash = hashlib.md5(normal_json.write_parquet()).hexdigest()

        log("[+] Bilateral IM data normalization successful")
    
    except Exception as e :

        log(f"[-] Error during bilateral IM data normalization: {e}", "error")

    return normal_json, md5_hash


def load_simm_data_from_ice (
        
        fund : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        rename_cols : Optional[Dict] = None,
        specific_cols : Optional[List] = None

    ) -> Tuple[Optional[pl.DataFrame], str] :
    """
    Load and preprocess SIMM data from the ICE API.

    This function wraps `fetch_raw_simm_data`, renames its columns, and filters them to keep only relevant ones.

    Args:
        date (datetime): The date for which to load SIMM data.
        fund (str): Fund identifier.
        rename_cols (dict): Mapping of raw API column names to desired standardized column names.
        specific_cols (list): List of final column names to retain in the resulting DataFrame.

    Returns:
        data_cols (pl.DataFrame | None) : Cleaned Polars DataFrame with renamed and filtered columns,
                             or None if the fetch fails.
    """
    # Default values
    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund

    rename_cols = SIMM_RENAME_COLUMNS if rename_cols is None else rename_cols
    specific_cols = list(SIMM_RENAME_COLUMNS.values()) if specific_cols is None else specific_cols

    # Fetch and get the SIMM
    try :

        data_df, md5 = fetch_raw_simm_data(date, fund)

    except Exception as e :

        log("[-] Error getting the SIMM data from API ICE...", "error")
        return None, None
    
    log("[+] SIMM data successfully got", "info")
    
    # Data handling (Rename columns)
    data_rename = data_df.rename(rename_cols)

    # Polars normally manages the "," (commas) by itself
    data_cols = data_rename[specific_cols]
    md5_hash = hashlib.md5(data_cols.write_parquet()).hexdigest()

    print(data_cols)

    return data_cols, md5_hash


@st.cache_data()
def load_simm_data_from_df (
        
        _df : pl.DataFrame,
        md5_hash : Optional[str] = None,
        rename_cols : Optional[Dict] = None,
        specific_cols : Optional[List] = None

) -> Optional[Tuple[pl.DataFrame, str]] :
    """
    
    """
    rename_cols = SIMM_RENAME_COLUMNS if rename_cols is None else rename_cols
    specific_cols = list(SIMM_RENAME_COLUMNS.values()) if specific_cols is None else specific_cols

    # Data handling (Rename columns)
    data_rename = _df.rename(rename_cols)

    # Polars normally manages the "," (commas) by itself
    data_cols = data_rename[specific_cols]
    md5_hash = hashlib.md5(data_cols.write_parquet()).hexdigest()

    print(data_cols)

    return data_cols, md5_hash


def update_simm_date_from_df (
        
        df : pl.DataFrame, 
        md5 : Optional[str] = None,
        fund : Optional[str] =  None,
        date : Optional[str | dt.datetime | dt.date] = None
    
    ) :
    """
    Update a given Polars DataFrame by appending new rows from ICE API for a specific date.

    Args:
        df (pl.DataFrame): Existing DataFrame to be updated.
        md5 (str | None): Optional MD5 hash (unused here but may be useful in your logic).
        fund (str | None): Fund identifier.
        date (str | datetime | date | None): Date to fetch new SIMM data for.

    Returns:
        pl.DataFrame: Updated DataFrame with new rows added.
    """
    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund

    rename_cols = SIMM_RENAME_COLUMNS if rename_cols is None else rename_cols
    specific_cols = list(SIMM_RENAME_COLUMNS.values()) if specific_cols is None else specific_cols

    # Fetch and get the SIMM
    try :

        data_df_date, _ = load_simm_data_from_ice(date, fund, rename_cols, specific_cols)

        if data_df_date is None :
            
            log("[-] No data returned from ICE API.", "error")
            return df, md5
        
    except Exception as e :

        log("[-] Error getting the SIMM data from API ICE...", "error")
        return df, md5
    
    # We have the data for the date missing (today's date by default)

    full_data_df = pl.concat([df, data_df_date])
    new_md5 = hashlib.md5(full_data_df.write_parquet()).hexdigest()

    return full_data_df, new_md5

