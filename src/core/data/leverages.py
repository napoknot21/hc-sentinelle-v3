from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt

from typing import Optional, Dict, List, Tuple

from src.utils.data_io import load_excel_to_dataframe
from src.utils.logger import log
from src.utils.formatters import date_to_str, str_to_date

from src.config.parameters import (
    LEVERAGES_COLUMNS, LEVERAGES_UNDERL_COLUMNS, LEVERAGES_TRADE_COLUMNS, 
    FUND_HV, LEVERAGES_ALL_FILENAME, 
    LEVERAGES_UNDERL_REGEX, LEVERAGES_TRADE_REGEX
)
from src.config.paths import LEVERAGES_FUNDS_DIR_PATHS, LEVERAGES_UNDERL_FUNDS_DIR_PATHS, LEVERAGES_TRADE_FUNDS_DIR_PATHS


def read_history_leverages (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        leverages_paths : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] : 
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    schema_overrides = LEVERAGES_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    filename = LEVERAGES_ALL_FILENAME if filename is None else filename
    
    leverages_paths = LEVERAGES_FUNDS_DIR_PATHS if leverages_paths is None else leverages_paths
    path = leverages_paths.get(fund)

    full_path = os.path.join(path, filename)

    try :

        dataframe, md5 = load_excel_to_dataframe(full_path, specific_cols=specific_cols, schema_overrides=schema_overrides)

    except Exception as e :

        log(f"[-] Error during reading leverage history file: {e}", "error")
        return None, None
    
    return dataframe, md5


def read_underlying_leverages (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        leverages_paths : Optional[Dict] = None,
        
        regex : Optional[re.Pattern] = None,
        schema_overrides : Optional[Dict] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    regex = LEVERAGES_UNDERL_REGEX if regex is None else regex
    schema_overrides = LEVERAGES_UNDERL_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    leverages_paths = LEVERAGES_UNDERL_FUNDS_DIR_PATHS if leverages_paths is None else leverages_paths
    dir_path = leverages_paths.get(fund)

    filename, date_str = find_most_recent_file_by_date(date, dir_path, regex) if filename is None else filename

    if filename is None  :
        return None, None
    
    full_path = os.path.join(dir_path, filename)
    
    try :
        
        dataframe, md5 = load_excel_to_dataframe(full_path, specific_cols=specific_cols, schema_overrides=schema_overrides)
        
        dataframe =  dataframe.with_columns(
            pl.lit(date_str).alias("Date")
        )

    except Exception as e :

        log("[-] Error loading Leverages per Underlying file", "error")
        return None, None
    
    return dataframe, md5


def read_trade_leverages (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        leverages_paths : Optional[Dict] = None,
        
        regex : Optional[re.Pattern] = None,
        schema_overrides : Optional[Dict] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    regex = LEVERAGES_TRADE_REGEX if regex is None else regex
    schema_overrides = LEVERAGES_TRADE_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    leverages_paths = LEVERAGES_TRADE_FUNDS_DIR_PATHS if leverages_paths is None else leverages_paths
    dir_path = leverages_paths.get(fund)

    filename, date_str = find_most_recent_file_by_date(date, dir_path, regex) if filename is None else filename

    if filename is None  :
        return None, None
    
    full_path = os.path.join(dir_path, filename)
    
    try :

        dataframe, md5 = load_excel_to_dataframe(full_path, specific_cols=specific_cols, schema_overrides=schema_overrides)

        dataframe = dataframe.with_columns(
            pl.lit(date_str).alias("Date")
        )

    except Exception as e :

        log("[-] Error loading Leverages per Underlying file", "error")
        return None, None
    
    return dataframe, md5


def find_most_recent_file_by_date (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None
    
    ) -> Tuple[Optional[str], Tuple[str]] :
    """
    Return
    """
    if not os.path.isdir(dir_abs_path) :
        return None, None
    
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
    


