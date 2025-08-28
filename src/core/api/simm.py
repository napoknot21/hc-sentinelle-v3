import os
import hashlib
import polars as pl
import datetime as dt
import streamlit as st

from typing import Optional, Dict, List, Tuple

from src.core.api.client import get_ice_calculator

from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_RENAME_COLUMNS
from src.utils.logger import log
from src.utils.formatters import date_to_str, dataframe_fingerprint


@st.cache_data(ttl=600, show_spinner=False)
def fetch_raw_simm_data (
    
        date : str | dt.datetime | None = None,
        fund : str | None = None,
    
    ) -> Tuple[Optional[pl.DataFrame], str] :
    """
    Fetch raw bilateral SIMM (ICE) and return (df, md5) or None.

    Args:
        date (datetime): The date for which to retrieve SIMM data.
        fund (str): Fund identifier used in the API call.

    Returns:
        normal_json (pl.DataFrame | None) : A normalized Polars DataFrame containing the SIMM data,
                             or None if the API call or normalization fails.

    Note:
        This function refers to the "get_simm()" precedent version.
    """
    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund

    fund_map = FUND_NAME_MAP # We need to hardcode this value in order to get cache parameters of this function
    fund_name = fund_map.get(fund)

    if not fund_name :

        log(f"[-] Fund '{fund}' not found in FUND_NAME_MAP", "error")
        return None
    
    # Ice API connexion
    try :

        calculator = get_ice_calculator()
        log(f"[+] ICE API client ready | fund={fund}→{fund_name} | date={date}", "info")

    except Exception as e :

        log(f"[-] ICE API init failed: {e}", "error")
        return None
    
    # Network bound
    try :

        bilateral_im = calculator.get_bilateral_im_ctpy(date, fund_name)
        
        if bilateral_im is None:
        
            log(f"[-] bilateral IM is None | fund={fund} | date={date}", "error")
            return None

    except Exception as e :

        log(f"[-] Error during bilateral IM request: {e}", "error")
        return None
    
    


    # Billateral Data request
    bilateral_im = calculator.get_bilateral_im_ctpy(date, fund_name)
    
    if bilateral_im is None :
        
        log("[!] Error during bilateral IM data request", "error")
        return None, None

    log("[+] Bilateral IM data request successful")

    try :

        # Dictionarry billateral IM normalization
        normal_json = pl.json_normalize(bilateral_im)

        if normal_json is None :

            log("[-] Error during bilateral IM data normalization", "error")
            return None, None
        
        md5_hash = hashlib.md5(normal_json.write_csv().encode()).hexdigest()

        log("[+] Bilateral IM data normalization successful")

        return normal_json, md5_hash
    
    except Exception as e :

        log(f"[-] Error during bilateral IM data normalization: {e}", "error")
        return None, None


@st.cache_data(ttl=600, show_spinner=False)
def load_simm_data_from_ice (
        
        date : str | dt.datetime = None,
        fund : str | None = None,
        rename_cols : Dict | None = None,
        specific_cols : List | None = None

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

        data, md5 = fetch_raw_simm_data(date, fund)

    except Exception as e :

        log("[-] Error getting the SIMM data from API ICE...", "error")
        return None, None
    
    log("[+] SIMM data successfully got", "info")
    
    # Data handling (Rename columns)
    data_rename = data.rename(rename_cols)

    # Polars normally manages the "," (commas) by itself
    data_cols = data_rename[specific_cols]
    md5_hash = hashlib.md5(data_cols.write_csv().encode()).hexdigest()

    print(data_cols)

    return data_cols, md5_hash

