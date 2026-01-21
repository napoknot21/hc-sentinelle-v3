from __future__ import annotations

import os
import re
import sys
import polars as pl

from src.config.env import load_dotenv
load_dotenv()

# --------------- LibApi ------------------

from src.config.paths import LIBAPI_ABS_PATH

sys.path.append(LIBAPI_ABS_PATH)
from libapi.config.parameters import CCYS_ORDER  # type: ignore


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
    #"FX Projected Last Expiry Date" : pl.Utf8,
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

    "Asset Class" : pl.Utf8,

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

    "Asset Class" : pl.Utf8,

    "Buy/Sell" : pl.Utf8,
    "Call/Put" : pl.Utf8,

    "Strike" : pl.Float64,

    "Termination Date" : pl.Date,

}


# ---------------- NAV ----------------


NAV_CUTOFF_DATE=os.getenv("NAV_CUTOFF_DATE")
NAV_HIST_NAME_DEFAULT=os.getenv("NAV_HIST_NAME_DEFAULT")

NAV_HISTORY_COLUMNS = {

    "Portfolio Name": pl.Utf8,
    "MV": pl.Float64,
    "MV/NAV%": pl.Float64,
    "Comment": pl.Utf8,
    "Date": pl.Date,

}

NAV_PORTFOLIO_COLUMNS = dict(list(NAV_HISTORY_COLUMNS.items())[:3])


NAV_PORTFOLIO_REGEX_PATTERN=os.getenv("NAV_PORTFOLIO_REGEX_PATTERN")
NAV_PORTFOLIO_REGEX = re.compile(NAV_PORTFOLIO_REGEX_PATTERN, re.IGNORECASE)


# ------------ Subred --------------

SUBRED_BOOK_HV=os.getenv("SUBRED_BOOK_HV")
SUBRED_BOOK_WR=os.getenv("SUBRED_BOOK_WR")

SUBRED_FILENAME_PATTERN=os.getenv("SUBRED_FILENAME_PATTERN")
SUBRED_RAW_FILENAME_PATTERN=os.getenv("SUBRED_RAW_FILENAME_PATTERN")

SUBRED_FILENAME_REGEX = re.compile(SUBRED_FILENAME_PATTERN, re.IGNORECASE)
SUBRED_RAW_FILENAME_REGEX = re.compile(SUBRED_RAW_FILENAME_PATTERN, re.IGNORECASE)

SUBRED_STRUCT_COLUMNS = {

    "deliveryDate" : pl.Utf8,
    "notional" : pl.Float64,
    "currency" : pl.Utf8

}


SUBRED_COLS_NEEDED = {

    "tradeLegCode" : pl.Utf8,
    "tradeDescription" : pl.Utf8,
    "tradeName" : pl.Utf8,
    "bookName" : pl.Utf8,
    "tradeType" : pl.Utf8,
    "instrument" : pl.Struct(SUBRED_STRUCT_COLUMNS)

}


SUBRED_COLUMNS_READ = {

    "tradeLegCode" : pl.Utf8,
    "tradeDescription" : pl.Utf8,
    "tradeName" : pl.Utf8,
    "bookName" : pl.Utf8,
    "tradeType" : pl.Utf8,
    #"instrument" : pl.Struct(SUBRED_STRUCT_COLUMNS)

}


SUBRED_BOOKS_FUNDS = {

    os.getenv("FUND_HV") : SUBRED_BOOK_HV, 
    os.getenv("FUND_WR") : SUBRED_BOOK_WR,

}


# ---------------- Performances ----------------


PERF_HARDCODED_VALUES = {

    os.getenv("FUND_HV") : [
        
        {
            "Year" : os.getenv("PERF_YEAR_HARDCODED_VALUE"),
            "Month" : os.getenv("PERF_MONTH_HARDCODED_VALUE"),
            "Value" : os.getenv("PERF_VALUE_HARDCODED_VALUE"),
        },

        {
            "Year" : os.getenv("PERF_YEAR_HARDCODED_VALUE_2"),
            "Month" : os.getenv("PERF_MONTH_HARDCODED_VALUE_2"),
            "Value" : os.getenv("PERF_VALUE_HARDCODED_VALUE_2"),
        },
        
    ]
}


PERF_DEFAULT_DATE=os.getenv("PERF_DEFAULT_DATE")
PERF_ALLOCATION_DATE=os.getenv("PERF_ALLOCATION_DATE")
PERF_BOOK_WR=os.getenv("PERF_BOOK_WR")

PERF_BOOKS_FUNS = {

    os.getenv("FUND_HV") : SUBRED_BOOK_HV,
    os.getenv("FUND_WR") : PERF_BOOK_WR

}

PERF_ASSET_CLASSES_HV_FX = list(os.getenv("PERF_ASSET_CLASSES_HV_FX").split(";"))
PERF_ASSET_CLASSES_HV_EQ = list(os.getenv("PERF_ASSET_CLASSES_HV_EQ").split(";"))
PERF_ASSET_CLASSES_HV_V = list(os.getenv("PERF_ASSET_CLASSES_HV_V").split(";"))

PERF_ASSET_CLASSES_WR_FX = list(os.getenv("PERF_ASSET_CLASSES_WR_FX").split(";"))
PERF_ASSET_CLASSES_WR_EQ = list(os.getenv("PERF_ASSET_CLASSES_WR_EQ").split(";"))

PERF_ASSET_CLASSES_FUNDS = {

    os.getenv("FUND_HV") : {

        "FX" :  PERF_ASSET_CLASSES_HV_FX,
        "Equity" : PERF_ASSET_CLASSES_HV_EQ,
        "Vault" : PERF_ASSET_CLASSES_HV_V

    },

    os.getenv("FUND_WR") : {

        "FX" :  PERF_ASSET_CLASSES_WR_FX,
        "Equity" : PERF_ASSET_CLASSES_WR_EQ,

    }

}

PERF_INITIAL_ALLOCATION = {

    "FX" : 0.3*0.25*40000000,
    "Equity" : 0.7*0.25*40000000,
    "Vault" : 0.75*40000000,

}

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


NAV_FUNDS_COLUMNS = {

    FUND_HV : "NAV Estimate",
    FUND_WR : "NAV Estimate Weighted by Time"
    
}

# ---------------- EXO HYBRID ----------------


X_HYBRID_COLUMNS = {

    "Portfolio Name" : pl.Utf8,
    "Asset Class" : pl.Utf8,
    "Trade Type" : pl.Utf8,
    "Instrument" : pl.Utf8,
    "Trade Code" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Trade Name" : pl.Utf8,
    "Counterparty" : pl.Utf8,
    "Remaining Notional" : pl.Float64,
    "MV" : pl.Float64,

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
    "Net Excess/Deficit" : pl.Float64

}

PAIRS = {

    

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

PAYMENTS_HV_FUND = os.getenv("PAYMENTS_HV_FUND")
PAYMENTS_WR_FUND = os.getenv("PAYMENTS_WR_FUND")

PAYMENTS_FUNDS = [

    PAYMENTS_HV_FUND,
    PAYMENTS_WR_FUND

]

PAYMENTS_ACCOUNT_1 = os.getenv("PAYMENTS_ACCOUNT_1")
PAYMENTS_ACCOUNT_2 = os.getenv("PAYMENTS_ACCOUNT_2")
PAYMENTS_ACCOUNT_3 = os.getenv("PAYMENTS_ACCOUNT_3")


PAYMENTS_ACCOUNTS = [

    PAYMENTS_ACCOUNT_1,
    PAYMENTS_ACCOUNT_2,
    PAYMENTS_ACCOUNT_3

]

PAYMENTS_BENEFICIARY_COLUMNS = {

    "Counterparty" : pl.Utf8,
    "Type Payment" : pl.Utf8,
    "Currency" : pl.Utf8,
    "Bank" : pl.Utf8,

    "Beneficiary Bank" : pl.Utf8,
    "Swift-Code" : pl.Utf8,
    "Swift-Code Beneficiary" : pl.Utf8,
    "IBAN" : pl.Utf8

}

PAYMENTS_EXCEL_COLUMNS = [

    "A",  # fund
    "C",  # acc
    "D",  # currency
    "E",  # amount
    "F",  # date
    "H",  # "SHA"
    "I",  # bank
    "M",  # reference
    "Q",  # iban
    "R",  # swift_bank
    "S",  # benif
    "X",  # swift_benif
    "Z",  # name

]

PAYMENTS_BENECIFIARY_SHEET_NAME = os.getenv("PAYMENTS_BENECIFIARY_SHEET_NAME")

PAYMENTS_CONCURRENCIES = CCYS_ORDER

PAYMENTS_COUNTERPARTIES = {

    os.getenv("PAYMENTS_COUNTERPARTY_GS") : {

        "initials" : "GS",
        "bank" : os.getenv("PAYMENTS_COUNTERPARTY_BANK_GS")

    },
    
    os.getenv("PAYMENTS_COUNTERPARTY_MS") : {
    
        "initials" : "MS",
        "bank" : os.getenv("PAYMENTS_COUNTERPARTY_BANK_MS")

    },

    os.getenv("PAYMENTS_COUNTERPARTY_SAXO") : {
        
        "initials": os.getenv("PAYMENTS_COUNTERPARTY_SAXO"),
        "bank" : os.getenv("PAYMENTS_COUNTERPARTY_BANK_SAXO")
        
    },

    os.getenv("PAYMENTS_COUNTERPARTY_UBS_L") : {
    
        "initials" : os.getenv("PAYMENTS_COUNTERPARTY_UBS_L"),
        "bank" : os.getenv("PAYMENTS_COUNTERPARTY_BANK_UBS_L")

    },

    os.getenv("PAYMENTS_COUNTERPARTY_UBS_E") : {
        
        "initials" : os.getenv("PAYMENTS_COUNTERPARTY_UBS_E"),
        "bank" : os.getenv("PAYMENTS_COUNTERPARTY_BANK_UBS_E")
    }

}

PAYMENTS_REFERENCES_CTPY = {

    "Margin Call" : {

        os.getenv("PAYMENTS_COUNTERPARTY_GS") : os.getenv("PAYEMENTS_REFERENCE_GS_MC"),
        os.getenv("PAYMENTS_COUNTERPARTY_MS") : os.getenv("PAYEMENTS_REFERENCE_MS_MC"),       

    },

    "Option Premium" : {

        os.getenv("PAYMENTS_COUNTERPARTY_GS") : os.getenv("PAYEMENTS_REFERENCE_GS_OP"),
        os.getenv("PAYMENTS_COUNTERPARTY_MS") : os.getenv("PAYEMENTS_REFERENCE_MS_OP"),

    },

    "Option Exercise" : {

        os.getenv("PAYMENTS_COUNTERPARTY_MS") : os.getenv("PAYEMENTS_REFERENCE_MS_OE"),

    },


}


PAYMENTS_TYPES_MARKET = {

    "Margin Call" : ["Margin Call"],
    "Option Premium" : ["FX", "Equity", "Margin Call"],
    "Option Exercise" : ["FX", "Equity", "Margin Call"]

}

PAYMENTS_EMAIL_TO = os.getenv("PAYMENTS_EMAIL_TO")
PAYMENTS_EMAIL_FROM = os.getenv("PAYMENTS_EMAIL_FROM")
PAYMENTS_EMAIL_CC = os.getenv("PAYMENTS_EMAIL_CC")

PAYMENTS_EMAIL_CCs = [

    PAYMENTS_EMAIL_CC,
    PAYMENTS_EMAIL_FROM

]

PAYMENTS_EMAIL_SUBJECT = os.getenv("PAYMENTS_EMAIL_SUBJECT")

PAYMENTS_RAW_BODY = os.getenv("PAYMENTS_EMAIL_BODY", "")
PAYMENTS_EMAIL_BODY = PAYMENTS_RAW_BODY.replace("\\n", "\n")

PAYMENTS_DIRECTIONS = ["Pay", "Receive"]

PAYMENTS_BOOK_HV = os.getenv("PAYMENTS_BOOK_HV")
PAYMENTS_BOOK_WR = os.getenv("PAYMENTS_BOOK_WR")

PAYMENTS_BOOKS = [PAYMENTS_BOOK_HV, SUBRED_BOOK_HV, PAYMENTS_BOOK_WR, SUBRED_BOOK_WR]


# ------------------ UBS Settlement ------------------

UBS_PAYMENTS_EXCEL_COLUMNS = [

    "B",  # fund
    "C",  # Trade Ref
    "D",  # Reason for Payment / Receive
    "E",  # Acc Nb
    "F",  # Ctpy / Broker
    "G",  # Pays/Receives
    "H",  # Amount
    "I",  # Currecy
    "J",  # Value Date
    "K",  # FX rate

    "M",  # Correspond BIC
    "N",  # IBAN
    "O",  # Benef BIC
    
]

UBS_PAYMENTS_TYPES = ["Option Premium", "Option Exercice"]
UBS_PAYMENTS_MARKET = ["FX", "Equity"]


# ------------------ Leverages ------------------


LEVERAGES_ALL_FILENAME=os.getenv("LEVERAGES_ALL_FILENAME")

LEVERAGES_COLUMNS = {

    "Gross Leverage" : pl.Float64,
    "Commitment Leverage" : pl.Float64,
    "Date" : pl.Datetime,
    "File" : pl.Utf8

}

LEVERAGES_UNDERL_REGEX_PATTERN=os.getenv("LEVERAGES_UNDERL_REGEX_PATTERN")
LEVERAGES_UNDERL_REGEX = re.compile(LEVERAGES_UNDERL_REGEX_PATTERN, re.IGNORECASE)

LEVERAGES_UNDERL_COLUMNS = {

    "Asset Class" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Gross Leverage" : pl.Float64,
    "Exposure % NAV" : pl.Float64

}

LEVERAGES_TRADE_REGEX_PATTERN=os.getenv("LEVERAGES_TRADE_REGEX_PATTERN")
LEVERAGES_TRADE_REGEX = re.compile(LEVERAGES_TRADE_REGEX_PATTERN, re.IGNORECASE)

LEVERAGES_TRADE_COLUMNS = {

    "Trade ID" : pl.Int64,
    "Asset Class" : pl.Utf8,
    "Trade Type" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Termination Date" : pl.Date,
    "Buy/Sell" : pl.Utf8,
    "Notional" : pl.Float64,
    "Call/Put" : pl.Utf8,
    "Strike" : pl.Float64,
    "Trigger" : pl.Float64,
    "Reference Spot" :  pl.Float64,
    "Counterparty" : pl.Utf8,
    "Gross Leverage" : pl.Float64,
    "Exposure % NAV" : pl.Float64

}

# ------------ Greeks --------------


GREEKS_DEFAULT_DATE=os.getenv("GREEKS_DEFAULT_DATE")

GREEKS_ALL_FILENAME=os.getenv("GREEKS_ALL_FILENAME")

GREEKS_COLUMNS = {

    "Underlying" : pl.Utf8,
    "Delta" : pl.Float64,
    "Gamma" : pl.Float64,
    "Vega" : pl.Float64,
    "Theta" : pl.Float64,
    "Date" : pl.Utf8,

}

GREEKS_ASSET_CLASSES = {

    "Equity" : os.getenv("GREEKS_UNDERL_EQ_RULE"),
    "FX" : os.getenv("GREEKS_UNDERL_FX_RULE"),
    
}

GREEKS_OVERVIEW_COLUMNS = {

    "Underlying" : pl.Utf8,
    "Delta" : pl.Float64,
    "Gamma" : pl.Float64,
    "Vega" : pl.Float64,
    "Theta" : pl.Float64,
}

GREEK_REGEX_PATTERN=os.getenv("GREEK_REGEX_PATTERN")
GREEKS_REGEX = re.compile(GREEK_REGEX_PATTERN, re.IGNORECASE)

GREEKS_RISKS_EQUITY_COLUMNS = {

    "Underlying" : pl.Utf8,
    "Delta" : pl.Float64,
    "Gamma" : pl.Float64,
    "Vega" : pl.Float64,
    "Theta" : pl.Float64,
    "Delta % NAV" : pl.Float64,
    "Gamma % NAV" : pl.Float64,
    "Vega % NAV" : pl.Float64,
    "Theta % NAV" : pl.Float64

}


GREEKS_CROSS_DELTA_REGEX_PATTERN=os.getenv("GREEKS_CROSS_DELTA_REGEX_PATTERN")
GREEKS_CROSS_DELTA_REGEX = re.compile(GREEKS_CROSS_DELTA_REGEX_PATTERN, re.IGNORECASE)

GREEKS_CROSS_GAMMA_REGEX_PATTERN=os.getenv("GREEKS_CROSS_GAMMA_REGEX_PATTERN")
GREEKS_CROSS_GAMMA_REGEX = re.compile(GREEKS_CROSS_GAMMA_REGEX_PATTERN, re.IGNORECASE)

GREEKS_DELTA_PNL_STRESS_REGEX_PATTERN=os.getenv("GREEKS_DELTA_PNL_STRESS_REGEX_PATTERN")
GREEKS_DELTA_PNL_STRESS_REGEX = re.compile(GREEKS_DELTA_PNL_STRESS_REGEX_PATTERN, re.IGNORECASE)

GREEKS_DELTA_PNL_STRESS_COLUMNS = {

    "Underlying" : pl.Utf8,
    "-3 x Sigma - P&L" : pl.Float64,
    "-2 x Sigma - P&L" : pl.Float64,
    "-1 x Sigma - P&L" : pl.Float64,
    "0 x Sigma - P&L" : pl.Float64,
    "1 x Sigma - P&L" : pl.Float64,
    "2 x Sigma - P&L" : pl.Float64,
    "3 x Sigma - P&L" : pl.Float64,

}

GREEKS_DELTA_STRESS_NAV_REGEX_PATTERN=os.getenv("GREEKS_DELTA_STRESS_NAV_REGEX_PATTERN")
GREEKS_DELTA_STRESS_NAV_REGEX = re.compile(GREEKS_DELTA_STRESS_NAV_REGEX_PATTERN, re.IGNORECASE)

GREEKS_DELTA_STRESS_NAV_COLUMNS = {

    "Underlying" : pl.Utf8,
    "-3 x Sigma % NAV" : pl.Float64,
    "-2 x Sigma % NAV" : pl.Float64,
    "-1 x Sigma % NAV" : pl.Float64,
    "0 x Sigma % NAV" : pl.Float64,
    "1 x Sigma % NAV" : pl.Float64,
    "2 x Sigma % NAV" : pl.Float64,
    "3 x Sigma % NAV" : pl.Float64,

}

GREEKS_DELTA_STRESS_ABS_REGEX_PATTERN=os.getenv("GREEKS_DELTA_STRESS_ABS_REGEX_PATTERN")
GREEKS_DELTA_STRESS_ABS_REGEX = re.compile(GREEKS_DELTA_STRESS_ABS_REGEX_PATTERN, re.IGNORECASE)

GREEKS_DELTA_STRESS_ABS_COLUMNS = {

    "Underlying" : pl.Utf8,
    "-3 x Sigma" : pl.Float64,
    "-2 x Sigma" : pl.Float64,
    "-1 x Sigma" : pl.Float64,
    "0 x Sigma" : pl.Float64,
    "1 x Sigma" : pl.Float64,
    "2 x Sigma" : pl.Float64,
    "3 x Sigma" : pl.Float64,

}

GREEKS_LONG_SHORT_DELTA_REGEX_PATTERN=os.getenv("GREEKS_LONG_SHORT_DELTA_REGEX_PATTERN")
GREEKS_LONG_SHORT_DELTA_REGEX = re.compile(GREEKS_LONG_SHORT_DELTA_REGEX_PATTERN, re.IGNORECASE)

GREEKS_LONG_SHORT_DELTA_COLUMNS = {

    "Underlying Asset" : pl.Utf8,
    "Long Delta(%)" : pl.Float64,
    "Average Strike Long" : pl.Float64,
    "Average Maturities Long" : pl.Float64,
    "Short Delta(%)" : pl.Float64,
    "Average Strike Short" : pl.Float64,
    "Average Maturities Short" : pl.Float64,
    "Net Delta (%)" : pl.Float64

}

GREEKS_GAMMA_PNL_REGEX_PATTERN=os.getenv("GREEKS_GAMMA_PNL_REGEX_PATTERN")
GREEKS_GAMMA_PNL_REGEX = re.compile(GREEKS_GAMMA_PNL_REGEX_PATTERN, re.IGNORECASE)

GREEKS_GAMMA_PNL_COLUMNS = {

    "Underlying" : pl.Utf8,
    "Gamma" : pl.Float64,
    "Theta" : pl.Float64,
    "P&L / 1 sigma" : pl.Float64,
    "P&L / 3 sigma" : pl.Float64,
    "STD" : pl.Float64

}

GREEKS_RISK_CREDIT_REGEX_PATTERN=os.getenv("GREEKS_RISK_CREDIT_REGEX_PATTERN")
GREEKS_RISK_CREDIT_REGEX = re.compile(GREEKS_RISK_CREDIT_REGEX_PATTERN, re.IGNORECASE)

GREEKS_RISK_CREDIT_COLUMNS = {

    "Underlying" : pl.Utf8,
    "CS01" : pl.Float64,
    "CS01 % NAV" : pl.Float64

}

GREEKS_VEGA_BUCKET_REGEX_PATTERN=os.getenv("GREEKS_VEGA_BUCKET_REGEX_PATTERN")
GREEKS_VEGA_BUCKET_REGEX = re.compile(GREEKS_VEGA_BUCKET_REGEX_PATTERN, re.IGNORECASE)

GREEKS_VEGA_BUCKET_COLUMNS = {

    "Underlying Asset" : pl.Utf8,
    "1w" : pl.Float64,
    "1w-1m" : pl.Float64,
    "1m-3m" : pl.Float64,
    "3m-6m" : pl.Float64,
    "6m-1y" : pl.Float64,
    ">1y" : pl.Float64,
    "Total" : pl.Float64
    
}


GREEKS_VEGA_STRESS_PNL_REGEX_PATTERN=os.getenv("GREEKS_VEGA_STRESS_PNL_REGEX_PATTERN")
GREEKS_VEGA_STRESS_PNL_REGEX = re.compile(GREEKS_VEGA_STRESS_PNL_REGEX_PATTERN, re.IGNORECASE)

GREEKS_VEGA_STRESS_PNL_COLUMNS = {

    "Asset Class" : pl.Utf8,
    "Underlying" : pl.Utf8,
    "Vega" : pl.Float64,
    "Vega P&L - moderate" : pl.Float64, 
    "Vega P&L - stress" : pl.Float64,
    "Vega P&L - extreme" : pl.Float64,

}


GREEKS_CONCENTRATION_REGEX_PATTERN=os.getenv("GREEKS_CONCENTRATION_REGEX_PATTERN")
GREEKS_CONCENTRATION_REGEX = re.compile(GREEKS_CONCENTRATION_REGEX_PATTERN, re.IGNORECASE)

GREEKS_CONCENTRATION_COLUMNS = {

    "Counterparty" : pl.Utf8,
    "MV" : pl.Float64,
    "MV/NAV%" : pl.Float64,
    "Compliance" : pl.Utf8
    
}

GREEKS_ASSET_CLASS_RULES = {

    "FX": ["Curncy"],
    "EQUITY": ["Equity", "Index"],

}



# ------------ Screeners --------------


SCREENERS_COLUMNS_FX = {

    "Trade Code" : pl.Utf8,
    "Trade Description" : pl.Utf8,
    
    "Portfolio Name" : pl.Utf8,

    "Underlying Asset" : pl.Utf8,
    "Instrument Type" : pl.Utf8,

    "Buy/Sell" : pl.Utf8,

    "Reference Spot" : pl.Float64,
    "Original Spot" : pl.Float64,
    #"FX ForwardRate" : pl.Float64,
    "Forward" : pl.Float64,
    "Forward Points" : pl.Float64,

    "Strike" : pl.Float64,
    "MV" : pl.Float64,
    #"Base Notional" : pl.Float64,
    "FX Delta Base" : pl.Float64,
    
    "Trade Date" : pl.Date ,
    "Termination Date" : pl.Date,

}

SCREENERS_COLUMNS_TARF = {

    # General information
    "Trade Code" : pl.Utf8,
    "Trade Description" : pl.Utf8,

    "Portfolio Name" : pl.Utf8,
    "Instrument Type" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Trade Date" : pl.Date ,
    "FX Next Fixing Date" : pl.Date,
    #"FX Projected Last Expiry Date" : pl.Date,
    "FX Remaining Target Term Per Base" : pl.Float64,
    "Expiry Date" : pl.Date,
    "Call/Put 1" :  pl.Utf8,

    # Amounts and notionals
    "Remaining Notional" : pl.Float64,
    #"Base Notional" : pl.Float64,
    "Notional 1 Base" : pl.Float64,
    "Total Premium" : pl.Float64,
    "MV" : pl.Float64,

    # Strat and price
    "Original Spot" : pl.Float64,
    "Reference Spot" : pl.Float64,
    "Strike 1" : pl.Float64,
    "Trigger" : pl.Float64,

    # Greeks 
    "FX Delta Base" : pl.Float64,
    "FX Gamma Base" : pl.Float64,
    "FX Theta Base" : pl.Float64,

    # Fixing and FX echéances
    "FX Remaining Number of Fixings" : pl.Int64,
    "FX Projected Number of Expiries Remaining" : pl.Int64,
    "FX Projected Payout at Next Fixing" : pl.Float64,

    # Performance & Accumulation
    "FX Accrued Target Term Per Base" : pl.Float64,
    "FX Total Accumulated Profit" : pl.Float64,
    "FX Remaining Notional" : pl.Float64,
    
}

SCREENERS_COLUMNS_TAIL = {

    "Trade Code" : pl.Utf8,
    "Trade Description" : pl.Utf8,
    "Instrument Type" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Expiry Date" : pl.Date,
    "Portfolio Name" : pl.Utf8,
    "MV" : pl.Float64

}

SCREENERS_REGEX_PATTERN=os.getenv("SCREENERS_REGEX_PATTERN")
SCREENERS_REGEX = re.compile(SCREENERS_REGEX_PATTERN, re.IGNORECASE)

SCREENER_TOKEN_EXCLUDE=os.getenv("SCREENER_TOKEN_EXCLUDE")

SCREENER_TOKEN_FILTER=os.getenv("SCREENER_TOKEN_FILTER")


# ------------ Concentration --------------


CONCENTRATION_COLUMNS = {

    "Counterparty" : pl.Utf8,
    "MV" : pl.Float64,
    "MV/NAV%" : pl.Float64

}

CONCENTRATION_REGEX_PATTERN=os.getenv("CONCENTRATION_REGEX_PATTERN")
CONCENTRATION_REGEX = re.compile(CONCENTRATION_REGEX_PATTERN, re.IGNORECASE)


# ------------ Realized Volatility ------------

VOL_REALIZED_HV_COLUMNS=os.getenv("VOL_REALIZED_HV_COLUMNS")
VOL_REALIZED_WR_COLUMNS=os.getenv("VOL_REALIZED_WR_COLUMNS")

VOL_REALIZED_FUNDS_COLS = {

    os.getenv("FUND_HV") : VOL_REALIZED_HV_COLUMNS,
    os.getenv("FUND_WR") : VOL_REALIZED_WR_COLUMNS,

}



# -------------- Trade Recap --------------

TRADE_RECAP_LAUNCHER_FILE=os.getenv("TRADE_RECAP_LAUNCHER_FILE")

TRADE_RECAP_RAW_FILE_REGEX_PATTERN = os.getenv("TRADE_RECAP_RAW_FILE_REGEX_PATTERN")
TRADE_RECAP_RAW_FILE_REGEX = re.compile(TRADE_RECAP_RAW_FILE_REGEX_PATTERN, re.IGNORECASE)


TRADE_RECAP_MIN_COLUMNS = {

    "tradeId" : pl.Int64,
    "tradeDescription" : pl.Utf8,
    "tradeName" : pl.Utf8,
    "tradeType" : pl.Utf8,
    "assetClass" : pl.Utf8,
    "bookId": pl.Int64,
    "bookName" : pl.Utf8,
    "counterparty" : pl.Utf8,
    "creationTime" : pl.Utf8,
    "originatingAction" : pl.Utf8,
    "originatingInstrumentType" : pl.Utf8,


}


TRADE_RECAP_MAX_COLUMNS = {



}



# -------------- Agreaggated Positions --------------

AGGREGATED_POSITIONS_COLUMNS = {

    "Asset Class" : pl.Utf8,
    "Counterparty" : pl.Utf8,
    "Portfolio Name" : pl.Utf8,
    "Underlying Asset" : pl.Utf8,
    "Trade Type" : pl.Utf8,
    "Product Name" : pl.Utf8,
    #"Issuer" : pl.Utf8,
    "Instrument Type" : pl.Utf8,
    "Product Code" : pl.Utf8,
    "Trade Date" : pl.Datetime,
    "Trade Code" : pl.Utf8,
    "Remaining Notional" : pl.Float64,
    "Termination Date" : pl.Datetime,
    "MV" : pl.Float64,

}