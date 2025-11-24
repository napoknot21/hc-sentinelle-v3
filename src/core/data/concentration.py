from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt

from typing import Optional, List, Dict, Tuple, Any

from src.config.parameters import FUND_HV, CONCENTRATION_COLUMNS, CONCENTRATION_REGEX
from src.config.paths import *
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str, str_to_date
from src.utils.logger import log


def read_ccty_concentration (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        concentration_paths : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,
        regex : Optional[re.Pattern] = None

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    schema_overrides = CONCENTRATION_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    regex = CONCENTRATION_REGEX if regex is None else regex
    
    concentration_paths = CONCENTRATION_FUNDS_DIR_PATHS if concentration_paths is None else concentration_paths
    dir_abs = concentration_paths.get(fund)

    filename, _ = find_most_recent_file_by_date (date, dir_abs, regex) if filename is None else filename
    
    if filename is None :
        return None, None
    
    full_path = os.path.join(dir_abs, filename)

    try :
        dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides, specific_cols=specific_cols)

    except Exception as e :

        log(f"[-] Error during concentration {date_to_str(date)} file reading", "error")
        return None, None
    
    return dataframe, md5


def find_most_recent_file_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None

    ) -> Tuple[Optional[str], Tuple[str]] :
    """
    
    """
    if not os.path.isdir(dir_abs_path) :
        return None, None
    
    date = date_to_str(date)
    regex = CONCENTRATION_REGEX  if regex is None else regex

    # Best pour la date cible
    best_target_key: Optional[tuple] = None   # (hh, mm, mtime)
    best_target_name: Optional[str] = None

    best_global_key: Optional[tuple] = None   # (date_str, hh, mm, mtime)
    best_global_name: Optional[str] = None

    date = date_to_str(date)

    with os.scandir(dir_abs_path) as it : # 
        
        for entry in it :

            if not entry.is_file() :
                continue

            m = regex.match(entry.name)

            if not m :
                continue

            date_str, hh, mm = m.groups()

            hh_i = int(hh)
            mm_i = int(mm)
            mtime = entry.stat().st_mtime

            if date_str == date :

                key_t = (hh_i, mm_i, mtime)
                
                if best_target_key is None or key_t > best_target_key :

                    best_target_key = key_t
                    best_target_name = entry.name

            key_g = (date_str, hh_i, mm_i, mtime)

            if best_global_key is None or key_g > best_global_key :

                best_global_key = key_g
                best_global_name = entry.name

    if best_target_name is not None :
        return best_target_name, date

    # Most recent file otherwise
    if best_global_name is not None :
        return best_global_name, key_g[0]

    return None, None
