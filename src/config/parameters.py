import os, sys
from src.config.env import load_dotenv

DEFAULT_TO_EMAIL=os.getenv("DEFAULT_TO_EMAIL")
DEFAULT_CC_EMAIL=os.getenv("DEFAULT_CC_EMAIL")
DEFAULT_FROM_EMAIL=os.getenv("DEFAULT_FROM_EMAIL")


FUND_NAME_MAP = {

    os.getenv("FUND_HV") : "HV",
    os.getenv("FUND_WR") : "WR"

}

