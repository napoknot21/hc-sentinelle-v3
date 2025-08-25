import os, sys
from src.config.env import load_dotenv


DEFAULT_TO_EMAIL=os.getenv("DEFAULT_TO_EMAIL")
DEFAULT_CC_EMAIL=os.getenv("DEFAULT_CC_EMAIL")
DEFAULT_FROM_EMAIL=os.getenv("DEFAULT_FROM_EMAIL")

FUND_WR=os.getenv("FUND_WR")
FUND_HV=os.getenv("FUND_HV")

SIMM_HIST_NAME=os.getenv("SIMM_HIST_NAME")

SIMM_CUTOFF_DATE=os.getenv("SIMM_CUTOFF_DATE")

FUND_NAME_MAP = {

    FUND_HV : "HV",
    FUND_WR : "WR",

}



