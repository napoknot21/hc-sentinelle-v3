from __future__ import annotations

import os
import re
import json
import polars as pl
import datetime as dt

from typing import Optional, Dict, List

from src.utils.formatters import date_to_str

from src.config.parameters import (
    FUND_HV,
    SUBRED_FILENAME_REGEX, SUBRED_RAW_FILENAME_REGEX, SUBRED_COLS_NEEDED,
    SUBRED_COLUMNS_READ, SUBRED_BOOKS_FUNDS, SUBRED_STRUCT_COLUMNS
)
from src.config.paths import SUBRED_AUM_CACHE_ABS_PATH

from src.utils.data_io import export_dataframe_to_excel, load_excel_to_dataframe

def read_aum_from_cache (
        
        date : Optional[str | dt.datetime | dt.date] = None, 
        filename : Optional[str] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

    ) :
    """
    
    """
    date = date_to_str(date)
    regex = SUBRED_FILENAME_REGEX if regex is None else regex

    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path
    filename = find_cache_file_by_date(date, regex=regex) if filename is None else filename

    if filename is None :
        return None
    
    full_path = os.path.join(dir_abs_path, filename)

    with open(full_path, "r+", encoding="utf-8") as f :
        data = json.load(f)

    return data


def read_detailed_aum_from_cache (
        
        date : Optional[str | dt.datetime | dt.date] = None,

        filename : Optional[str] = None,
        dir_abs_path : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        schema_overrides : Optional[Dict] = None,

    ) :
    """
    Docstring for read_detailed_aum_from_cache
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param filename: Description
    :type filename: Optional[str]
    :param dir_abs_path: Description
    :type dir_abs_path: Optional[str]
    :param regex: Description
    :type regex: Optional[re.Pattern]
    """
    date = date_to_str(date)
    regex = SUBRED_RAW_FILENAME_REGEX if regex is None else regex

    schema_overrides = SUBRED_COLUMNS_READ if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path
    filename = find_raw_aum_filename_cache_by_date(date, regex=regex) if filename is None else filename

    if filename is None :
        return None, None
    
    full_path = os.path.join(dir_abs_path, filename)

    try :
        datafame , md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides)

    except :

        print("[-] Error during reading")
        return None, None

    print(datafame)
    return datafame, md5


def clean_aum_by_fund (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund : Optional[str]= None,
        books_by_fund : Optional[Dict] = None,

        column_to_explode : Optional[str] = None,
        schema_override : Optional[Dict] = None,

    
    ) :
    """
    Docstring for clean_aum_by_fund
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    :param fund: Description
    :type fund: Optional[str]
    """
    fund = FUND_HV if fund is None else fund
    books_by_fund = SUBRED_BOOKS_FUNDS if books_by_fund is None else books_by_fund

    book = books_by_fund.get(fund)

    column_to_explode = "instrument" if column_to_explode is None else column_to_explode
    schema_override = SUBRED_STRUCT_COLUMNS if schema_override is None else schema_override

    dataframe = dataframe.filter(pl.col("bookName") == book)
    dataframe = dataframe.drop("bookName")

    if dataframe.schema.get(column_to_explode) == pl.Utf8 :

        dataframe =  dataframe.with_columns(
            pl.col(column_to_explode)
              .cast(pl.Utf8)
              .str.replace_all("'", '"')               # -> JSON valide
              .str.json_decode(pl.Struct(schema_override))           # -> Struct
              .alias(column_to_explode)
        )

    dataframe = dataframe.with_columns(
        pl.col(column_to_explode)
          .struct.rename_fields(list(schema_override.keys()))
          .alias(column_to_explode)
    )

    dataframe = dataframe.with_columns(
        [
            pl.col(column_to_explode)
            .struct.field(field_name)
            .alias(field_name)
            .cast(dtype)
            for field_name, dtype in schema_override.items()
        ]
    )

    dataframe = dataframe.drop("instrument")
    dataframe = dataframe.with_columns(
        pl.col("deliveryDate").str.strptime(pl.Date, strict=False)
    )
    
    dataframe = dataframe.sort("deliveryDate", descending=True)
    
    return dataframe, md5


def find_cache_file_by_date (

        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,    

    ) -> Optional[str] :
    """
    
    """
    date = date_to_str(date)
    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path
    regex = SUBRED_FILENAME_REGEX if regex is None else regex

    os.makedirs(dir_abs_path, exist_ok=True)

    with os.scandir(dir_abs_path) as it : 
        
        for entry in it :

            if not entry.is_file() :
                continue

            m = regex.match(entry.name)

            if not m :
                continue
            
            date_str = m.groups()

            if date_str[0] == date :
                return entry.name

    return None


def find_raw_aum_filename_cache_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

    ) :
    """
    Docstring for find_raw_um_cache_by_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param regex: Description
    :type regex: Optional[re.Pattern]
    """
    date = date_to_str(date)

    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path
    regex = SUBRED_RAW_FILENAME_REGEX if regex is None else regex

    os.makedirs(dir_abs_path, exist_ok=True)

    with os.scandir(dir_abs_path) as it : 
        
        for entry in it :

            if not entry.is_file() :
                continue

            m = regex.match(entry.name)

            if not m :
                continue

            date_str = m.groups()

            if date_str[0] == date :
                return entry.name

    return None


def save_aum_to_cache (
        
        aum_dict : Dict,
        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None
        
    ) -> bool :
    """
    
    """
    date = date_to_str(date)
    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path

    os.makedirs(dir_abs_path, exist_ok=True)

    if aum_dict is None :

        print("\n[-] Nothing was saved. Continuing...")
        return False
    
    filename = f"{date}_aum.json"
    full_path = os.path.join(dir_abs_path, filename)

    try :

        # Write JSON file
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(aum_dict, f, indent=4)

    except Exception as e :
     
        return False
    
    return True 

    
def save_raw_aum_to_cache (
        
        dataframe : Optional[pl.DataFrame] = None,

        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None

    ) :
    """
    Docstring for save_raw_aum_to_cache
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param dir_abs_path: Description
    :type dir_abs_path: Optional[str]
    """
    date = date_to_str(date)
    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path

    os.makedirs(dir_abs_path, exist_ok=True)

    if dataframe is None :

        print("\n[-] Nothing was saved. Continuing...")
        return False
    
    filename = f"{date}_aum_raw.xlsx"
    full_path = os.path.join(dir_abs_path, filename)

    status = export_dataframe_to_excel(dataframe, output_abs_path=full_path)
        
    return status.get("success")