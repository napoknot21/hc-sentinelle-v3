from datetime import datetime as dt

from src.config.parameters import FUND_NAME_MAP
from src.core.api.client import get_ice_calculator
from src.utils.formatters import *
from src.utils.logger import log


RENAME_COLUMNS_SIMM = {

    "postIm" : "IM", 
    "post.price" :'MV', 
    "post.priceCapped" : "MV Capped", 
    "post.priceCappedMode" :"MV Capped Type",
    'group' : "Counterparty",
    'post.shortfall' : "Available / Shortfall Amount",
    "post.clientMarginRatio" : "Client Margin Rate"

}


def get_simm (date : str, fund : str) :
    """
    Call the ICE API to fetch bilateral SIMM data for a given fund and date.

    Args:
        date (str | datetime): The date of evaluation.
        fund (str): Fund name, e.g., "Heroics Volitility Fund".

    Returns:
        pd.DataFrame: Normalized SIMM data from the API.
    """
    try :
        ice_calc = get_ice_calculator()
        fund_name = FUND_NAME_MAP.get(fund, "WR")

        log("[+] Successfully connected to the API ICE", "info")

    except Exception as e :

        log(f"[-] Error during connexion to the API ICE: {e}", "error")
        
        return None

    # Billateral Data request
    bilateral_im = ice_calc.get_billateral_im_ctpy(date, fund=fund_name)
    
    if bilateral_im is None or bilateral_im == {} :
        
        log("[-] Error during bilateral IM data request", "error")
        return None

    log("[+] Bilateral IM data request successful")

    # Dictionarry billateral IM normalization
    normal_json = pd.json_normalize(bilateral_im)

    if normal_json is None :

        log("[-] Error during bilateral IM data normalization", "error")
        return None

    log("[+] Bilateral IM data normalization successful")

    return normal_json


def get_simm_data (date, fund) :
    """
    
    """
    data = get_simm(date, fund)

    renamed_data = data.rename(
        
        columns={
            
            "postIm"

        }

    )
