from __future__ import annotations

import os
from src.config.env import load_dotenv

load_dotenv()

LIBAPI_ABS_PATH=os.getenv("LIBAPI_PATH")
LOGS_DIR_PATH=os.getenv("LOGS_DIR_PATH")

MESSAGE_SAVE_DIRECTORY=os.getenv("MESSAGE_SAVE_DIRECTORY")

PAYMENTS_DIR_PATH=os.getenv("PAYMENTS_DIR_PATH")

# -------- SIMM paths -------- 

SIMM_FUND_HV_DIR_PATH=os.getenv("SIMM_FUND_HV_DIR_PATH")
SIMM_FUND_WR_DIR_PATH=os.getenv("SIMM_FUND_WR_DIR_PATH")

# The left side correspond the full fundation name
SIMM_FUNDS_DIR_PATHS = {

    os.getenv("FUND_HV") : SIMM_FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : SIMM_FUND_WR_DIR_PATH

}


# -------- Expiries Paths --------  

EXPIRIES_FUND_HV_DIR_PATH=os.getenv("EXPIRIES_FUND_HV_DIR_PATH")
EXPIRIES_FUND_WR_DIR_PATH=os.getenv("EXPIRIES_FUND_WR_DIR_PATH")

EXPIRIES_FUNDS_DIR_PATHS = {

    os.getenv("FUND_HV") : EXPIRIES_FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : EXPIRIES_FUND_WR_DIR_PATH

}


# -------- NAV Paths -------- 

NAV_FUND_HV_DIR_PATH=os.getenv("NAV_FUND_HV_DIR_PATH")
NAV_FUND_WR_DIR_PATH=os.getenv("NAV_FUND_WR_DIR_PATH")

NAV_FUNDS_DIR_PATHS = {

    os.getenv("FUND_HV") : EXPIRIES_FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : EXPIRIES_FUND_WR_DIR_PATH

}


# -------- NAV Estimate Paths ----------

NAV_ESTIMATE_FUND_HV_DIR_PATH=os.getenv("NAV_ESTIMATE_FUND_HV_DIR_PATH")
NAV_ESTIMATE_FUND_WR_DIR_PATH=os.getenv("NAV_ESTIMATE_FUND_WR_DIR_PATH")

NAV_ESTIMATE_FUNDS_DIR_PATHS = {

    os.getenv("FUND_HV") : NAV_ESTIMATE_FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : NAV_ESTIMATE_FUND_WR_DIR_PATH,

}

# -------- Cash --------

CASH_FUND_HV_FILE_PATH=os.getenv("CASH_FUND_HV_FILE_PATH")
CASH_FUND_WR_FILE_PATH=os.getenv("CASH_FUND_WR_FILE_PATH")

CASH_FUNDS_FILE_PATHS = {

    os.getenv("FUND_HV") : CASH_FUND_HV_FILE_PATH,
    os.getenv("FUND_WR") : CASH_FUND_WR_FILE_PATH

}

# -------- Cash --------

COLLATERAL_FUND_HV_DIR_PATH=os.getenv("COLLATERAL_FILE_ABS_PATH")


# -------- Payments --------

PAYMENTS_DB_ABS_PATH=os.getenv("PAYMENTS_DB_ABS_PATH")
PAYMENTS_DB_REL_PATH=os.getenv("PAYMENTS_DB_REL_PATH")

SECURITIES_DB_ABS_PATH=os.getenv("SECURITIES_DB_ABS_PATH")
SECURITIES_DB_REL_PATH=os.getenv("SECURITIES_DB_REL_PATH")