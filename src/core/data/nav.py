from __future__ import annotations

import os
import hashlib
import polars as pl
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str

from src.config.parameters import FUND_HV, NAV_COLUMNS, NAV_HIST_NAME_DEFAULT, NAV_CUTOFF_DATE
from src.config.paths import NAV_FUND_HV_DIR_PATH, NAV_FUNDS_DIR_PATHS


def read_history_nav_from_excel (
        
        fund : Optional[str] = None,
        nav_fund_paths : Optional[Dict] = None,
        schema_overrides : Optional[Dict] = None,
        specific_cols : Optional[List] = None,
        cutoff_date : Optional[str] = None
        
    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    Read historiacal NAV data for a fiven path to the fund's SIMM Excel file
    
    """
    excel_file_abs_path = get_nav_abs_path_by_fund(fund, nav_fund_paths)

    schema_overrides = NAV_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys()) if specific_cols is None else specific_cols
    cutoff_date = NAV_CUTOFF_DATE if cutoff_date is None else cutoff_date

    if excel_file_abs_path is None :

        log(f"[-] NAV {excel_file_abs_path} does not exist or not found.")
        return None, None

    try :

        nav_history_df, _ = load_excel_to_dataframe(excel_file_abs_path, specific_cols=specific_cols, schema_overrides=schema_overrides)

        if nav_history_df is None :

            log("[-] No data returned from the NAV file", "error")
            return None, None
        
    except Exception as e :
        
        log(f"[-] Error getting the NAV data : {e}", "error")
        return None, None
    
    cutoff_date_parsed = dt.datetime.strptime(cutoff_date, "%Y-%m-%d").date()

    if "Date" in nav_history_df.columns :

        nav_history_df = nav_history_df.filter(pl.col("Date") >= pl.lit(cutoff_date_parsed))
        md5_hash = hashlib.md5(nav_history_df.write_parquet()).hexdigest()
        
        log(f"[+] NAV file read successfully")

    else :
        
        log(f"[!] 'Date' column not found in DataFrame. Cannot apply cutoff.", "warning")

    return nav_history_df, md5_hash


def treat_string_nav_cols_df (
    
        _df : pl.DataFrame,
        md5_hash : Optional[str] = None,
        string_cols : Optional[List[str]] = None

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    string_cols = [col for col, dtype in NAV_COLUMNS.items() if dtype == pl.Utf8] if string_cols is None else string_cols

    _df = (
        _df.with_columns(
            [
                pl.when(pl.col(col) == "nan").then(None).otherwise(pl.col(col)).alias(col)
                for col in string_cols
            ]
        )
    )

    md5_new = hashlib.md5(_df.write_parquet()).hexdigest()

    return _df, md5_new


def is_nav_history_updated_from_df (
        
        _df : pl.DataFrame,
        md5_hash : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        specific_col : str = "Date"

    ) -> bool :
    """
    
    """
    if _df is None :

        log("[-] The dataframe is NULL. Impossible to get information.","error")
        return False

    date_str = date_to_str(date)
    lastest_date = _df.select(specific_col).to_series()[-1] # Specific for the last date (today's date)

    if lastest_date == date_str :

        log("[*] Dataframe and NAV excel already updated with today's date !")
        return True

    return False


def is_nav_history_updated_from_file (
        
        fund : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        specific_col : str = "Date"

    ) -> bool :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    date = date_to_str(date)

    df_nav, md5_hash = read_history_nav_from_excel(fund)
    is_updated = is_nav_history_updated_from_df(df_nav, md5_hash, date, specific_col)

    return is_updated


def get_nav_abs_path_by_fund (
        
        fund : Optional[str] = None,
        nav_fund_paths : Optional[Dict] = None,
        basename_file : Optional[str] = None
    
    ) -> Optional[str] :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    nav_fund_paths = NAV_FUNDS_DIR_PATHS if nav_fund_paths is None else nav_fund_paths 
    
    fund_abs_path = nav_fund_paths.get(fund, NAV_FUND_HV_DIR_PATH)
    basename_file = NAV_HIST_NAME_DEFAULT if basename_file is None else basename_file

    nav_abs_path = os.path.join(fund_abs_path, basename_file)

    return nav_abs_path