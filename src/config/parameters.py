import os, sys
from dotenv import load_dotenv

load_dotenv()

LIBAPI_PATH_WINDOWS=os.getenv("LIBAPI_PATH_WINDOWS")
LIBAPI_PATH_LINUX=os.getenv("LIBAPI_PATH_LINUX")
