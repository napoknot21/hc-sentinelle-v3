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


def load_upcomming_expiries (
    
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,

        return_date : bool = False,

        regex : Optional[re.Pattern | str] = None,
        fund_map : Optional[Dict] = None,

        schema_override : Optional[Dict[str, Any]] = None,

        file_abs_path : Optional[str] = None,
    
    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = date_to_str(date)

    fund_map = FUND_NAME_MAP if fund_map is None else fund_map
    
    fundation = FUND_HV if fundation is None else fundation
    fundation_name = fund_map.get(fundation) # This is initial (HV, etc)
    
    schema_override = (EXPIRIES_COLUMNS_HV if fundation_name == "HV" else EXPIRIES_COLUMNS) if schema_override is None else schema_override
    columns_list = list(schema_override.keys())

    regex = EXPIRIES_FILENAME_REGEX if regex is None else regex

    file_abs_path = get_upcomming_expiries_file_by_date (date, fundation, regex=regex)
    print(file_abs_path)
    
    if file_abs_path is None :        
        log("[-] File does not exist for the specific date", "error")
    
    # Dataframe content and md5hash for content caching
    dataframe, md5 = load_excel_to_dataframe(file_abs_path, specific_cols=columns_list, schema_overrides=schema_override)

    if dataframe is None :
        log("[-] Error during reading excel file operation", "error")
    
    else :

        log("[+] FIle successfully read and converted to DataFrame")
        print(dataframe)

    return dataframe, md5


def get_upcomming_expiries_file_by_date (

        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,

        format : str = "%Y-%m-%d",

        regex : Optional[re.Pattern | str] = None,
        exp_dict_paths : Optional[Dict[str, str]] = None,

    ) -> Optional[str] :
    """
    
    """
    exp_dict_paths = EXPIRIES_FUNDS_DIR_PATHS if exp_dict_paths is None else exp_dict_paths
    regex = EXPIRIES_FILENAME_REGEX if regex is None else regex

    date = date_to_str(date, format)
    target_date = dt.datetime.strptime(date, format).date()

    dir_abs_path = exp_dict_paths.get(fundation)

    if not dir_abs_path:
            return None
    
    base = Path(dir_abs_path)

    if not base.exists() or not base.is_dir() :
        return None
    
    best_exact: Optional[Tuple[Tuple[int, int], float, str]] = None
    best_before: Optional[Tuple[Tuple[int, int, int, int], float, str]] = None

    with os.scandir(base) as it :

        for entry in it :

            if not entry.is_file() :
                continue

            m = regex.match(entry.name)

            if not m :
                continue

            file_date_s = m.group(1)        # 'YYYY-MM-DD'
            hhmm_s = m.group(2)              # 'HH-MM' (strict)
            parts = hhmm_s.split("-")

            if len(parts) != 2 :
                continue

            try :

                file_date = dt.datetime.strptime(file_date_s, "%Y-%m-%d").date()
                hh, mm = int(parts[0]), int(parts[1])
            
            except ValueError :
                continue

            mtime = entry.stat().st_mtime

            if file_date == target_date :

                key_exact = (hh, mm)
                
                if (best_exact is None) or (key_exact > best_exact[0]) or (
                    key_exact == best_exact[0] and mtime > best_exact[1]
                ) :
                    best_exact = (key_exact, mtime, entry.path)

            elif file_date < target_date :

                key_before = (file_date.year, file_date.month, file_date.day, hh * 100 + mm)
                
                if (best_before is None) or (key_before > best_before[0]) or (
                    key_before == best_before[0] and mtime > best_before[1]
                ):
                    best_before = (key_before, mtime, entry.path)

    if best_exact is not None :
        return str(Path(best_exact[2]).resolve())

    if best_before is not None :
        return str(Path(best_before[2]).resolve())

    return None



    
