from __future__ import annotations

import os
import re
import time
import hashlib
import polars as pl
import datetime as dt
import streamlit as st

from typing import Optional, List, Dict, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str, str_to_date, filter_token_col_from_df, exclude_token_cols_from_df, filter_groupby_col_from_df
from src.utils.data_io import load_excel_to_dataframe
from src.config.parameters import (
    FUND_HV, SCREENERS_COLUMNS_FX, SCREENERS_COLUMNS_TARF, SCREENERS_REGEX,
    SCREENERS_COLUMNS_TAIL, SCREENER_TOKEN_EXCLUDE, SCREENER_TOKEN_FILTER,
    AGGREGATED_POSITIONS_COLUMNS

)
from src.config.paths import SCREENERS_FUNDS_DIR_PATHS


def read_db_gross_data_by_date (
        
        date : Optional[ str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

        schema_overrides : Optional[Dict] = None,
        leverages_paths : Optional[Dict] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    Docstring for read_db_gross_data_by_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fund: Description
    :type fund: Optional[str]
    :param regex: Description
    :type regex: Optional[re.Pattern]
    :param schema_overrides: Description
    :type schema_overrides: Optional[Dict]
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    regex = SCREENERS_REGEX if regex is None else regex

    schema_overrides = AGGREGATED_POSITIONS_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    leverages_paths = SCREENERS_FUNDS_DIR_PATHS if leverages_paths is None else leverages_paths
    dir_path = leverages_paths.get(fund)

    filename, real_date = find_most_recent_file_by_date(date, dir_path, regex) if filename is None else (filename, date)

    if filename is None :
        return None, None
    
    full_path = os.path.join(dir_path, filename)
    
    try :
        dataframe, md5 = load_excel_to_dataframe(full_path, "Trade Legs", specific_cols=specific_cols, schema_overrides=schema_overrides)

    except Exception as e :

        log("[-] Error loading Leverages per Underlying file", "error")
        return None, None

    return dataframe, md5, real_date


def asset_class_cascade_by_date (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 :  Optional[str] = None,
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        schema_overrides : Optional[Dict] = None,

        asset_class : str = "CASH"


    ) -> Tuple[Optional[pl.DataFrame], Optional[str], Optional[str | dt.datetime | dt.date]] :
    """
    Docstring for cash_cascade_by_date
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    regex = SCREENERS_REGEX if regex is None else regex
    schema_overrides = AGGREGATED_POSITIONS_COLUMNS if schema_overrides is None else schema_overrides

    _dataframe, md5, real_date = read_db_gross_data_by_date(date, fund, regex=regex, schema_overrides=schema_overrides) if _dataframe is None else (_dataframe, md5, date)
    
    _dataframe = _dataframe.filter(pl.col("Asset Class") == (asset_class))

    return _dataframe, md5, real_date


def tarf_visualizer_by_date (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,
        
        regex : Optional[re.Pattern] = None,

        schema_overrides :  Optional[Dict] = None,
        columns_filter : List[str] = ["Instrument Type", "Expiry Date", "Underlying Asset"],

        token_exclude : Optional[str] = None,
        token_filter : Optional[str] = None

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    regex = SCREENERS_REGEX if regex is None else regex
    schema_overrides = SCREENERS_COLUMNS_TARF if schema_overrides is None else schema_overrides

    _dataframe, md5, real_date = read_db_gross_data_by_date(date, fund, regex) if _dataframe is None else (_dataframe, md5, date)

    _dataframe = _dataframe.select([col for col in schema_overrides if col in _dataframe.columns])

    token_exclude = SCREENER_TOKEN_EXCLUDE if token_exclude is None else token_exclude
    token_filter = SCREENER_TOKEN_FILTER if token_filter is None else token_filter

    df_filtered = filter_token_col_from_df(_dataframe, columns_filter[0], token_filter)
    #df_ordered = filter_order_col_from_df(df_filtered, "Expiry Date")
    df_grouped = filter_groupby_col_from_df(df_filtered, columns_filter[1])

    print(df_grouped)

    return df_grouped, md5, real_date


def find_most_recent_file_by_date (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None,

        regex : Optional[re.Pattern] = None
    
    ) -> Tuple[Optional[str], Optional[str]] :
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

            ts = m.group(1)               # ex: "20241121T093001.123"

            date_str = ts[0:8]            # "20241121"
            hh = ts[9:11]                 # "09"
            mm = ts[11:13]                # "30"

            if date_str == date :

                key_t = (date_str, hh, mm)
                
                if best_target_key is None or key_t > best_target_key :

                    best_target_key = key_t
                    best_target_name = entry.name

            key_g = (date_str, hh, mm, ts)

            if best_global_key is None or key_g > best_global_key :

                best_global_key = key_g
                best_global_name = entry.name

    if best_target_name is not None :
        return best_target_name, date

    # Most recent file otherwise
    if best_global_name is not None :
        return best_global_name, key_g[0]

    return None, None



