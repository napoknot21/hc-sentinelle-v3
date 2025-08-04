import polars as pl
import datetime as dt

from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_HIST_NAME
from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.core.api.client import get_ice_calculator

from src.utils.data_io import load_excel_to_dataframe
from src.utils.logger import log


RENAME_COLUMNS_SIMM = {

    'group' : "Counterparty",

    "postIm" : "IM",

    "post.price" :'MV',
    "post.priceCapped" : "MV Capped",
    "post.priceCappedMode" :"MV Capped Type",
    'post.shortfall' : "Available / Shortfall Amount",
    "post.clientMarginRatio" : "Client Margin Rate",

}


def get_simm (date : dt.datetime, fund : str = FUND_HV) -> pl.DataFrame | None :
    """
    Call the ICE API to fetch bilateral SIMM data for a given fund and date.

    Args:
        date (str | datetime): The date of evaluation. In format 'YYY-MM-DD HH:mm:ss'
        fund (str): Fund name

    Returns:
        pl.DataFrame: Normalized SIMM data from the API.
    """
    try :

        ice_calc = get_ice_calculator()
        fund_name = FUND_NAME_MAP.get(fund)

        if not fund_name :

            log(f"[-] Fund '{fund}' not found in FUND_NAME_MAP", "error")
            return None

        log("[+] Successfully connected to the API ICE", "info")

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


def get_simm_data (date : dt.datetime, fund : str = FUND_HV) : 
    """
    
    """
    # Fetch and get the SIMM
    try :

        data = get_simm(date, fund)

    except Exception as e :

        log("[-] Error getting the SIMM data...", "error")
        return None
    
    log("[+] Data get successfully", "info")
    
    # Data handling (Rename columns)
    data_rename = data.rename(RENAME_COLUMNS_SIMM)

    # Polars normally manages the "," (commas) by itself
    cols = list(RENAME_COLUMNS_SIMM.values())
    data_cols = data_rename[cols]

    return data_cols


def find_all_simm_history (fund : str = FUND_HV, relative_filename : str = SIMM_HIST_NAME, type = int) :
    """
    Function to get all leverages from the leverage folder and save them in a single file.
    """
    fundation_path = SIMM_FUNDS_DIR_PATHS[fund] # Check for the fundation path
    abs_excel_file = fundation_path + relative_filename # Get the /path/to/the/file.extension

    simm_history_df = load_excel_to_dataframe(abs_excel_file)

    # TO DO

    return simm_history_df



# results = get_simm_data(dt.datetime.now(), FUND_HV)


