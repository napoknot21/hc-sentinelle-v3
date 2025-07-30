import os
import pandas as pd
import xlwings as xw

from src.config.parameters import *


def excel_to_dataframe (file_path, sheet_name=None) -> pd.DataFrame :
    """
    
    """
    if not check_if_exists(file_path) :
        return None

    return 












def check_if_exists (filename) :
    """
    This private function checks if the file exists
    """
    return os.path.isfile(filename)
