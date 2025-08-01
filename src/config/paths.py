import os, pathlib
from src.config.env import load_dotenv

LIBAPI_PATH_WINDOWS=os.getenv("LIBAPI_PATH_WINDOWS")
LIBAPI_PATH_LINUX=os.getenv("LIBAPI_PATH_LINUX")

if os.name == "nt":
    LIBAPI_PATH = pathlib.Path(LIBAPI_PATH_WINDOWS)
else :
    LIBAPI_PATH = pathlib.Path(LIBAPI_PATH_LINUX)


LOG_DIR=os.getenv("LOG_DIR")

MESSAGE_SAVE_DIRECTORY=os.getenv("MESSAGE_SAVE_DIRECTORY")