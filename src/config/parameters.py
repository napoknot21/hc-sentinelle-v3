import os, sys
import polars as pl

from src.config.env import load_dotenv
load_dotenv()

# Azure info for Microsoft Graph API
CLIENT_ID=os.getenv("CLIENT_ID") # or APP_ID
CLIENT_SECRET_VALUE=os.getenv("CLIENT_SECRET_VALUE")
CLIENT_SECRET_ID=os.getenv("CLIENT_SECRET_ID") # Not useful
TENANT_ID=os.getenv("TENANT_ID") # or DIRECTORY_ID

EMAIL_URL_GET_TOKEN=os.getenv("EMAIL_URL_GET_TOKEN")
EMAIL_URL_SEND_MAIL=os.getenv("EMAIL_URL_SEND_MAIL")

# Defaults for Email
DEFAULT_TO_EMAIL=os.getenv("DEFAULT_TO_EMAIL")
DEFAULT_CC_EMAIL=os.getenv("DEFAULT_CC_EMAIL")
DEFAULT_FROM_EMAIL=os.getenv("DEFAULT_FROM_EMAIL")


# -------- Fundations --------

FUND_WR=os.getenv("FUND_WR")
FUND_HV=os.getenv("FUND_HV")

FUND_NAME_MAP = {

    FUND_HV : "HV",
    FUND_WR : "WR",

}


# -------- SIMM values -------

SIMM_HIST_NAME_DEFAULT=os.getenv("SIMM_HIST_NAME")
SIMM_CUTOFF_DATE=os.getenv("SIMM_CUTOFF_DATE") 

SIMM_COLUMNS = {

    "group" : { 
    
        "name" : "Counterparty",
        "type": pl.Utf8 
    
    },

    "postIm" : {
    
        "name" : "IM",
        "type" : pl.Float64
    
    },

    "post.price" : {
        
        "name" : "MV",
        "type" : pl.Float64
    
    },
    
    "post.priceCapped" : {
    
        "name" : "MV Capped",
        "type" : pl.Float64
    
    },

    "post.priceCappedMode" : {
    
        "name" : "MV Capped Type",
        "type" : pl.Utf8
    
    },
    
    'post.shortfall' : {
    
        "name" : "Available / Shortfall Amount",
        "type" : pl.Float64
    
    },

    "post.clientMarginRatio" : {
    
        "name" : "Client Margin Rate",
        "type" : pl.Float64
    
    },

}

# Mapping: raw_name -> final_name
SIMM_RENAME_COLUMNS : dict[str, str] = {k: v["name"] for k, v in SIMM_COLUMNS.items()}

# -------- FX Screeners (Tarf) --------

TARF_COLUMNS={

    # General information
    "Portfolio Name" : pl.Utf8,
    "Instrument Type" : pl.Utf8,
    "Trade Code" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Trade Date" : pl.Utf8 ,
    "FX Next Fixing Date" : pl.Utf8,
    "FX Remaining Target Term Per Base" : pl.Float64,
    "Expiry Date" : pl.Utf8,
    "Call/Put 1" :  pl.Utf8,

    # Amounts and notionals
    "Remaining Notional" : pl.Float64,
    "Base Notional" : pl.Int64,
    "Total Premium" : pl.Float64,
    "MV" : pl.Float64,
    "Total Expiries" : pl.Int64,

    # Strat and price
    "Original Spot" : pl.Float64,
    "Reference Spot" : pl.Float64,
    "Strike" : pl.Float64,
    "Trigger" : pl.Float64,

    # Greeks 
    "FX Delta Base" : pl.Float64,
    "FX Gamma Base" : pl.Float64,
    "Theta" : pl.Float64,

    # Fixing and FX echéances
    "FX Remaining Number of Fixings" : pl.Int64,
    "FX Projected Number of Expiries Remaining" : pl.Int64,
    "FX Projected Last Expiry Date" : pl.Utf8,
    "FX Projected Payout at Next Fixing" : pl.Float64,

    # Performance & Accumulation
    "FX Accrued Target Term Per Base" : pl.Float64,
    "FX Total Accumulated Profit" : pl.Float64,
    "FX Remaining Notional" : pl.Float64,
    
}


# -------- Expiries --------

EXPIRIES_COLUMNS = {

    "Trade Type" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Termination Date" : pl.Utf8,

    "Buy/Sell" : pl.Utf8,
    "Notional" : pl.Utf8,
    "Portfolio Name" : pl.Utf8,
    "Call/Put" : pl.Utf8,

    "Strike" : pl.Float64,
    "Trigger" : pl.Float64,

    "Reference Spot" : pl.Float64,
    "Counterparty" : pl.Utf8,
    "MV" : pl.Utf8,
    "Total Premium" : pl.Utf8,

    "Days Remaining" : pl.UInt64,

}

EXPIRIES_COLUMNS_HV = EXPIRIES_COLUMNS.copy()
EXPIRIES_COLUMNS_HV.update({"Trigger 2" : pl.Float64, "As Of" : pl.Utf8})