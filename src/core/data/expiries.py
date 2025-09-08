from __future__ import annotations

import os
import re
import time
import datetime as dt
import polars as pl

from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str, get_most_recent_file, get_most_recent_file_for_date
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
        regex : Optional[re.Pattern | str] = None
    
    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    fund_map = FUND_NAME_MAP if fund_map is None else fund_map
    fundation = FUND_HV if fundation is None else fundation
    fundation_name = fund_map.get(fundation) # This is initial (HV, etc)
    
    schema_override = (EXPIRIES_COLUMNS_HV if fundation_name == "HV" else EXPIRIES_COLUMNS) if schema_override is None else schema_override
    columns_list = list(schema_override.keys()) if columns_list is None else columns_list

    regex = EXPIRIES_FILENAME_REGEX if regex is None else regex

    file_abs_path = get_most_recent_file_for_date(date, fundation, EXPIRIES_FUNDS_DIR_PATHS, regex) if file_abs_path is None else file_abs_path
    
    if file_abs_path is None :
        
        log("[-] File does not exist for the specific date", "error")

        file_abs_path = get_most_recent_file(fundation, EXPIRIES_FUNDS_DIR_PATHS, regex)
        
        log("[+] Recalculating most recent available file")
    
    # Dataframe content and md5hash for content caching
    dataframe, md5 = load_excel_to_dataframe(file_abs_path, specific_cols=columns_list, schema_overrides=schema_override)

    if dataframe is None :
        log("[-] Error during reading excel file operation", "error")
    
    else :

        log("[+] FIle successfully read and converted to DataFrame")
        print(dataframe)

    return dataframe, md5


def get_upcomming_expiries_from_df (
        
        df : pl.DataFrame,
        date : str | dt.datetime,
        fundation : str,
        md5 : str | None = None
    
    ) :
    """
    
    """
    return None




