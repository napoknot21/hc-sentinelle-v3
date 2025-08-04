import os, pathlib
from src.config.env import load_dotenv


LIBAPI_PATH = pathlib.Path("LIBAPI_PATH")

LOG_DIR=os.getenv("LOG_DIR")

MESSAGE_SAVE_DIRECTORY=os.getenv("MESSAGE_SAVE_DIRECTORY")


FUND_HV_DIR_PATH=os.getenv("FUND_HV_DIR_PATH")
FUND_WR_DIR_PATH=os.getenv("FUND_WR_DIR_PATH")


FUND_DIR_PATHS = {

    os.getenv("FUND_HV") : FUND_HV_DIR_PATH,
    os.getenv("FUND_WR") : FUND_WR_DIR_PATH

}