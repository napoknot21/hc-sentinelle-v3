from __future__ import annotations

import os
import re
import time
import datetime as dt
import polars as pl

from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str
from src.utils.data_io import load_excel_to_dataframe

from src.config.parameters import FUND_HV, EXPIRIES_COLUMNS, EXPIRIES_COLUMNS_HV, FUND_NAME_MAP, EXPIRIES_FILENAME_REGEX
from src.config.paths import EXPIRIES_FUNDS_DIR_PATHS


def load_upcomming_expiries_from_file (
    
        file_abs_path : Optional[str] = None,
        date : str | dt.datetime = None,
        fundation : Optional[str] = None,
        return_date : bool = False,
        schema_override : Optional[Dict[str, Any]] = None,
        columns_list : Optional[List[str]] = None,
        fund_map : Optional[Dict] = None,
    
    ) -> Optional[pl.DataFrame] :
    """
    
    """
    file_abs_path = get_most_recent_file_for_date(date, fundation) if file_abs_path is None else file_abs_path
    
    if file_abs_path is None :
        
        log("[-] File does not exist for the specific date", "error")

        file_abs_path = get_most_recent_file(fundation)
        log("[+] Recalculating most recent available file")
    
    fund_map = FUND_NAME_MAP if fund_map is None else fund_map
    fundation = FUND_HV if fundation is None else fundation
    fundation_name = fund_map.get(fundation)

    schema_override = (EXPIRIES_COLUMNS_HV if fundation_name == "HV" else EXPIRIES_COLUMNS) if schema_override is None else schema_override
    columns_list = list(schema_override.keys()) if columns_list is None else columns_list
    
    dataframe = load_excel_to_dataframe(file_abs_path, specific_cols=columns_list, schema_overrides=schema_override)

    if dataframe is None :
        log("[-] Error during reading excel file operation", "error")
    
    else :
        log("[+] FIle successfully read and converted to DataFrame")

    return dataframe


def get_upcomming_expiries_from_df (_df : pl.DataFrame, date : str | dt.datetime, fundation : str = "HV", md5 : str | None = None) :
    """
    
    """
    return None




