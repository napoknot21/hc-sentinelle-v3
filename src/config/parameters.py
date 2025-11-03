from __future__ import annotations

import os, re
import polars as pl

from src.config.env import load_dotenv
load_dotenv()

# ---------------- MS Azure ----------------

# Azure info for Microsoft Graph API
CLIENT_ID=os.getenv("CLIENT_ID") # or APP_ID
CLIENT_SECRET_VALUE=os.getenv("CLIENT_SECRET_VALUE")
CLIENT_SECRET_ID=os.getenv("CLIENT_SECRET_ID") # Not useful
TENANT_ID=os.getenv("TENANT_ID") # or DIRECTORY_ID

EMAIL_URL_GET_TOKEN=os.getenv("EMAIL_URL_GET_TOKEN")
EMAIL_URL_SEND_MAIL=os.getenv("EMAIL_URL_SEND_MAIL")

# Defaults for Email
EMAIL_DEFAULT_TO=os.getenv("EMAIL_DEFAULT_TO")
EMAIL_DEFAULT_CC=os.getenv("EMAIL_DEFAULT_CC")
EMAIL_DEFAULT_FROM=os.getenv("EMAIL_DEFAULT_FROM")


# ---------------- Fundations ----------------

FUND_WR=os.getenv("FUND_WR")
FUND_HV=os.getenv("FUND_HV")

FUND_NAME_MAP = {

    FUND_HV : "HV",
    FUND_WR : "WR",

}


# ---------------- SIMM values ----------------

SIMM_HIST_NAME_DEFAULT=os.getenv("SIMM_HIST_NAME_DEFAULT")
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


# ---------------- FX Screeners (Tarf) ----------------

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


# ---------------- Expiries ----------------

EXPIRIES_FILENAME_REGEX = re.compile(r"^expiries_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})")

EXPIRIES_COLUMNS = {

    "Trade Type" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Termination Date" : pl.Date,

    "Buy/Sell" : pl.Utf8,
    "Notional" : pl.Float64,

    "Call/Put" : pl.Utf8,

    "Strike" : pl.Float64,
    "Trigger" : pl.Float64,

    "Reference Spot" : pl.Float64,
    "Counterparty" : pl.Utf8,

    "MV" : pl.Float64,
    "Total Premium" : pl.Float64,

    "Trigger 2" : pl.Float64,

    "Days Remaining" : pl.UInt64,

    "As Of" : pl.Utf8,
}

EXPIRIES_COLUMNS_HV = EXPIRIES_COLUMNS.copy()
EXPIRIES_COLUMNS_HV.update(
    {
        
        "Portfolio Name" : pl.Utf8,
        "Strike 1" : pl.Float64,
        "Strike 2" : pl.Float64,

    }
)

EXPIRIES_COLUMNS_SPECIFIC = {

    "Trade Type" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,

    "Buy/Sell" : pl.Utf8,
    "Call/Put" : pl.Utf8,

    "Strike" : pl.Float64,

    "Termination Date" : pl.Date,

}


# ---------------- NAV ----------------

NAV_CUTOFF_DATE=os.getenv("NAV_CUTOFF_DATE")
NAV_HIST_NAME_DEFAULT=os.getenv("NAV_HIST_NAME_DEFAULT")

NAV_COLUMNS = {

    "Portfolio Name": pl.Utf8,
    "MV": pl.Float64,
    "MV/NAV%": pl.Float64,
    "Comment": pl.Utf8,
    "Date": pl.Date,

}


# ---------------- Performances ----------------

PERF_DEFAULT_DATE=os.getenv("PERF_DEFAULT_DATE")


# ---------------- NAV Estimate ----------------

NAV_ESTIMATE_CUTOFF_DATE=os.getenv("NAV_ESTIMATE_CUTOFF_DATE")
NAV_ESTIMATE_HIST_NAME_DEFAULT=os.getenv("NAV_ESTIMATE_HIST_NAME_DEFAULT")

NAV_ESTIMATE_COLUMNS = {

    "NAV Estimate": pl.Float64,
    "NAV Estimate Weighted by Time": pl.Float64,
    "date": pl.Date,

}

NAV_ESTIMATE_RENAME_COLUMNS = {

    "NAV Estimate" : "GAV",
    "NAV Estimate Weighted by Time" : "Weighted Performance"

}


# ---------------- Cash ----------------

CASH_COLUMNS = {

    "Fundation" : pl.Utf8,
    "Account" : pl.Utf8,
    "Date" : pl.Date,
    "Bank" : pl.Utf8,
    "Currency" : pl.Utf8,
    "Type" : pl.Utf8,
    "Amount in CCY" : pl.Float64,
    "Exchange" : pl.Float64,
    "Amount in EUR" : pl.Float64

}

COLLATERAL_COLUMNS = {

    "Fundation" : pl.Utf8,
    "Account" : pl.Utf8,
    "Date" : pl.Date,
    "Bank" : pl.Utf8,
    "Currency" : pl.Utf8,
    "Total" : pl.Float64,
    "IM" : pl.Float64,
    "VM" : pl.Float64,
    "Requirement" : pl.Float64,
    "Net Exess/Deficit" : pl.Float64

}


# ---------------- Payments ----------------

PAYMENTS_COLUMNS = {

    "Fondsname" : pl.Utf8,
    
    #"KA" : pl.Utf8,
    "KONTONR" : pl.Int64,
    "DEVISE" : pl.Utf8,
    "BETRAG" : pl.Float64,
    "VALUTA" : pl.Datetime,
    "AUFTRAGGEBER" : pl.Utf8,
    "SPESENDETAIL" : pl.Utf8,
    
    "BEGUENSTIGTER" : pl.Utf8,
    #"BEGUENSTIGTER.1" : pl.Utf8,
    #"BEGUENSTIGTER.2" : pl.Utf8,
    #"BEGUENSTIGTER.3" : pl.Utf8,

    "ZAHLUNGSTEXT" : pl.Utf8,
    #"ZAHLUNGSTEXT.1" : pl.Utf8,
    #"ZAHLUNGSTEXT.2" : pl.Utf8,
    #"ZAHLUNGSTEXT.3" : pl.Utf8,

    "IBAN" : pl.Utf8,

    "MIT BANK" : pl.Utf8,
    "MIT BANK.1" : pl.Utf8,
    #"MIT BANK.2" : pl.Utf8,
    #"MIT BANK.3" : pl.Utf8,

    #"NOSTROKONTO" : pl.Utf8,
    #"BEAUFTR. BANK" : pl.Utf8,
    "KORRESPONDENT" : pl.Utf8,

    #"UEBERTR.-SPESEN" : pl.Utf8,
    "TEXT KONTOAUSZUG" : pl.Utf8

}

SECURITIES_COLUMNS = {

    "Transref. AM" : pl.Int64,
    "fund" : pl.Utf8,
    
    "NEWM/CANC" : pl.Utf8,
    "Portfolio ID  AM" : pl.Int64,
    "BUY/SELL" : pl.Utf8,
    
    "Quantity" : pl.Int64,
    
    "Sec. ID" : pl.Utf8,
    "Sec. name" : pl.Utf8,

    "Price" : pl.Float64,
    "Trade CCY" : pl.Utf8,

    "Interest" : pl.Float64,

    "Trade date" : pl.Datetime,
    "Settlement date" : pl.Datetime,

    "Sett. CCY" : pl.Utf8,

    "Broker ID" : pl.Utf8,
    "Settl. amount" : pl.Float64

}

