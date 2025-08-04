import os
from src.config.env import load_dotenv


LIBAPI_PATH=os.getenv("LIBAPI_PATH")
LOG_DIR=os.getenv("LOG_DIR")

MESSAGE_SAVE_DIRECTORY=os.getenv("MESSAGE_SAVE_DIRECTORY")


FUND_HV_DIR_PATH=os.getenv("FUND_HV_DIR_PATH")
FUND_WR_DIR_PATH=os.getenv("FUND_WR_DIR_PATH")


SIMM_FUND_HV_DIR_PATH=os.getenv("SIMM_FUND_HV_DIR_PATH")
SIMM_FUND_WR_DIR_PATH=os.getenv("SIMM_FUND_WR_DIR_PATH")


# The left side correspond the full fundation name
FUND_DIR_PATHS = {

    os.getenv("FUND_HV") : FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : FUND_WR_DIR_PATH

}


# The left side correspond the full fundation name
SIMM_FUNDS_DIR_PATHS = {

    os.getenv("FUND_HV") : SIMM_FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : SIMM_FUND_WR_DIR_PATH

}