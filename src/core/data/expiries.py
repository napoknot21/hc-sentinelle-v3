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

from src.config.parameters import FUND_HV, EXPIRIES_COLUMNS, EXPIRIES_COLUMNS_HV, FUND_NAME_MAP
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



def get_most_recent_file_for_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        directory_map : Optional[Dict] = None,
        extension : str = ".xlsx", 
        regex : Optional[re.Pattern] = None,
    
    ) -> Optional[str] :
    """
    
    """
    start = time.time()

    fundation = FUND_HV if fundation is None else fundation
    date = date_to_str(date)
    target_day = dt.datetime.strptime(date, "%Y-%m-%d").date()

    directory_map = EXPIRIES_FUNDS_DIR_PATHS if directory_map is None else directory_map
    dir_abs_path = directory_map.get(fundation)

    regex = re.compile(r"^expiries_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})") if regex is None else regex

    # Track best candidate as (timestamp, path)
    best_ts : Optional[dt.datetime] = None
    best_path : Optional[Path] = None

    root = Path(dir_abs_path)
    with os.scandir(root) as it :

        for entry in it :

            if not entry.is_file() :
                continue

            name = entry.name

            if not name.lower().endswith(extension) :
                continue

            stem = os.path.splitext(name)[0]
            m = regex.match(stem)

            if not m :
                continue

            day_str, hhmm_str = m.group(1), m.group(2)

            try :

                d = dt.datetime.strptime(day_str, "%Y-%m-%d").date()
                t = dt.datetime.strptime(hhmm_str, "%H-%M").time()

            except ValueError :

                continue

            if d != target_day :
                continue

            ts = dt.datetime.combine(d, t)

            if (best_ts is None) or ts > best_ts :

                best_ts = ts
                best_path = Path(entry.path)

    log(f"[*] Search done in {time.time() - start:.2f} seconds")
    
    return best_path


def get_most_recent_file (
    
        fundation : Optional[str] = None,
        directory_map : Optional[Dict] = None,
        extension : str = ".xlsx",
        regex : Optional[re.Pattern] = None
    
    ) -> Optional[str] :
    """
    
    """
    start = time.time()

    regex = re.compile(r"^expiries_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})") if regex is None else regex
    fundation = FUND_HV if fundation is None else fundation

    directory_map = EXPIRIES_FUNDS_DIR_PATHS if directory_map is None else directory_map
    dir_abs_path = directory_map.get(fundation)

    root = Path(dir_abs_path)

    # Track best candidate as (timestamp, path)
    best_ts : Optional[dt.datetime] = None
    best_path : Optional[Path] = None

    with os.scandir(root) as it :

        for entry in it :

            if not entry.is_file() :
                continue

            name = entry.name

            if not name.lower().endswith(extension) :
                continue

            stem = os.path.splitext(name)[0]
            m = regex.match(stem)

            if not m :
                continue
            
            day_str, hhmm_str = m.group(1), m.group(2)

            try :

                d = dt.datetime.strptime(day_str, "%Y-%m-%d").date()
                t = dt.datetime.strptime(hhmm_str, "%H-%M").time()

            except ValueError :

                continue

            ts = dt.datetime.combine(d, t)

            if (best_ts is None) or ts > best_ts :

                best_ts = ts
                best_path = Path(entry.path)

    log(f"[*] Search most recent file done in {time.time() - start:.2f} seconds")
    
    return best_path
