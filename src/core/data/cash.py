from __future__ import annotations

import os
import hashlib
import datetime as dt
import polars as pl

from typing import Optional, Dict

from src.config.paths import CASH_FUNDS_FILE_PATHS
from src.config.parameters import CASH_COLUMNS

from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str


def load_all_cash (
        
        date : Optional[str | dt.date | dt.datetime],
        fundation : str,

        schema_override : Optional[Dict] =  None,
        dir_dict_fund : Optional[Dict[str, str]] = None
        
    ) : 
    """
    
    """
    date = date_to_str(date)

    schema_override = CASH_COLUMNS if schema_override is None else schema_override
    columns = list(schema_override.keys())

    dir_dict_fund = CASH_FUNDS_FILE_PATHS if dir_dict_fund is None else dir_dict_fund

    filename = get_cash_file_per_fundation(fundation, dir_dict_fund)

    if filename is None :
        return None
    
    dataframe, md5 = load_excel_to_dataframe(filename, specific_cols=columns, schema_overrides=schema_override, cast_num=False)

    return dataframe, md5


def load_cash_by_date (
    
        date : Optional[str | dt.date | dt.datetime],
        fundation : str,

        schema_override : Optional[Dict] =  None
    
    ) :
    """
    
    """
    date = date_to_str(date)

    schema_override = CASH_COLUMNS if schema_override is None else schema_override
    columns = list(schema_override.keys())

    filename = get_cash_file_per_fundation(fundation)

    if filename is None :
        return None
    
    dataframe, md5 = load_excel_to_dataframe(filename, specific_cols=columns, schema_overrides=schema_override, cast_num=False)

    df_date = dataframe.filter(pl.col("Date") == date)

    csv_bytes = df_date.write_csv().encode("utf-8")
    md5_hash_date = hashlib.md5(csv_bytes).hexdigest()

    return df_date, md5_hash_date


def get_cash_file_per_fundation (fundation : str, dir_dict_fund : Optional[Dict[str, str]] = None) -> Optional[str] :
    """
    
    """
    dir_dict_fund = CASH_FUNDS_FILE_PATHS if dir_dict_fund is None else dir_dict_fund

    filename = dir_dict_fund.get(fundation)

    if filename is None or not os.path.exists(filename) :
        return None
    
    return filename


