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


# Fundations
FUND_WR=os.getenv("FUND_WR")
FUND_HV=os.getenv("FUND_HV")

FUND_NAME_MAP = {

    FUND_HV : "HV",
    FUND_WR : "WR",

}


# SIMM values
SIMM_HIST_NAME=os.getenv("SIMM_HIST_NAME")
SIMM_CUTOFF_DATE=os.getenv("SIMM_CUTOFF_DATE")


SIMM_COLUMNS = {

    "group" : { "name" : "Counterparty", "type": pl.Utf8 },

    "postIm" : { "name" : "IM", "type" : pl.Float64 },

    "post.price" : { "name" : "MV", "type" : pl.Float64 },
    "post.priceCapped" : { 'name' : 'MV Capped', 'type' : pl.Float64 },
    "post.priceCappedMode" : { "name" : "MV Capped Type", "type" : pl.Utf8 },
    'post.shortfall' : { "name" : "Available / Shortfall Amount", "type" : pl.Float64 },
    "post.clientMarginRatio" : { "name" : "Client Margin Rate", "type" : pl.Float64 },

}