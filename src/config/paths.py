import os
from src.config.env import load_dotenv

load_dotenv()

LIBAPI_ABS_PATH=os.getenv("LIBAPI_PATH")
LOGS_DIR_PATH=os.getenv("LOGS_DIR_PATH")

MESSAGE_SAVE_DIRECTORY=os.getenv("MESSAGE_SAVE_DIRECTORY")


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