import os, sys
from src.config.env import load_dotenv

# Azure info for Microsoft Graph API
CLIENT_ID=os.getenv("CLIENT_ID") # or APP_ID
CLIENT_SECRET_VALUE=os.getenv("CLIENT_SECRET_VALUE")
CLIENT_SECRET_ID=os.getenv("CLIENT_SECRET_ID") # Not useful
TENANT_ID=os.getenv("TENANT_ID") # or DIRECTORY_ID

URL_AUTH_TOKEN=os.getenv("URL_AUTH_TOKEN")


# Default
DEFAULT_TO_EMAIL=os.getenv("DEFAULT_TO_EMAIL")
DEFAULT_CC_EMAIL=os.getenv("DEFAULT_CC_EMAIL")
DEFAULT_FROM_EMAIL=os.getenv("DEFAULT_FROM_EMAIL")

<<<<<<< HEAD
FUND_WR=os.getenv("FUND_WR")
=======


>>>>>>> bed43af6d0288839d083f048787087518b10752c
FUND_HV=os.getenv("FUND_HV")



SIMM_HIST_NAME=os.getenv("SIMM_HIST_NAME")
SIMM_CUTOFF_DATE=os.getenv("SIMM_CUTOFF_DATE")


FUND_NAME_MAP = {

    FUND_HV : "HV",
    FUND_WR : "WR",

}



