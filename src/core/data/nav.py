from __future__ import annotations

import os
import math
import hashlib
import calendar
import polars as pl
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str, str_to_date

from src.config.parameters import (
    FUND_HV, NAV_COLUMNS, NAV_HIST_NAME_DEFAULT, NAV_CUTOFF_DATE,
    NAV_ESTIMATE_HIST_NAME_DEFAULT, NAV_ESTIMATE_COLUMNS, NAV_ESTIMATE_RENAME_COLUMNS,
    NAV_FUNDS_COLUMNS
)
from src.config.paths import NAV_PORTFOLIO_FUND_HV_DIR_PATH, NAV_PORTFOLIO_FUNDS_DIR_PATHS, NAV_ESTIMATE_FUNDS_DIR_PATHS


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

        nav_history_df, md5 = load_excel_to_dataframe(excel_file_abs_path, specific_cols=specific_cols, schema_overrides=schema_overrides)

        if nav_history_df is None :

            log("[-] No data returned from the NAV file", "error")
            return None, None
        
    except Exception as e :
        
        log(f"[-] Error getting the NAV data : {e}", "error")
        return None, None
    
    cutoff_date_parsed = str_to_date(cutoff_date)

    if "Date" in nav_history_df.columns :
        
        nav_history_df = nav_history_df.filter(pl.col("Date") >= pl.lit(cutoff_date_parsed))
        log(f"[+] NAV file read successfully")

    else :
        
        log(f"[!] 'Date' column not found in DataFrame. Cannot apply cutoff.", "warning")

    return nav_history_df, md5


def read_nav_estimate_by_fund (
        
        fundation : Optional[str] = None,

        filename : Optional[str] = None,
        fund_dict : Optional[Dict[str, str]] = None,
        
        schema_override : Optional[Dict] = None
    
    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    fundation = FUND_HV if fundation is None else fundation
    fund_dict = NAV_ESTIMATE_FUNDS_DIR_PATHS if fund_dict is None else fund_dict

    dir_abs_path = fund_dict.get(fundation)
    filename = NAV_ESTIMATE_HIST_NAME_DEFAULT if filename is None else filename

    fullname = os.path.join(dir_abs_path, filename)
    schema_override = NAV_ESTIMATE_COLUMNS if schema_override is None else schema_override
    columns = list(schema_override.keys())

    dataframe, md5 = load_excel_to_dataframe(fullname, schema_overrides=schema_override, specific_cols=columns)

    return dataframe, md5


def rename_nav_estimate_columns (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        original_cols : Optional[Dict] = None,
        rename_cols : Optional[Dict] = None,

        fundation : Optional[str] = None,
        forward_fill :  bool = True

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    dataframe, md5 = read_nav_estimate_by_fund(fundation) if dataframe is None else dataframe, md5

    original_cols = NAV_ESTIMATE_COLUMNS if original_cols is None else original_cols
    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols

    dataframe = dataframe.with_columns(
        [
            pl.col(c).cast(dtype, strict=False).alias(c)
            for c, dtype in original_cols.items()
            if c in dataframe.columns
        ]
    )

    rename_valid = {k: v for k, v in rename_cols.items() if k in dataframe.columns}
    dataframe = dataframe.rename(rename_valid)

    if forward_fill :
            
        dataframe = dataframe.with_columns(
            [
                pl.col(list(rename_cols.values())).forward_fill()
            ]
        )

    return dataframe, md5


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
    nav_fund_paths = NAV_PORTFOLIO_FUNDS_DIR_PATHS if nav_fund_paths is None else nav_fund_paths 
    
    fund_abs_path = nav_fund_paths.get(fund, NAV_PORTFOLIO_FUND_HV_DIR_PATH)
    basename_file = NAV_HIST_NAME_DEFAULT if basename_file is None else basename_file

    nav_abs_path = os.path.join(fund_abs_path, basename_file)

    return nav_abs_path


def estimated_gross_performance (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund :  Optional[str] = None,
        columns_fund : Optional[Dict] = None,
    
    ) :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    dataframe, md5 = read_nav_estimate_by_fund(fund) if dataframe is None else dataframe
    
    columns_fund = NAV_FUNDS_COLUMNS if columns_fund is None else columns_fund
    column = columns_fund.get(fund)

    #specific_cols = [column, "date"]
    #dataframe = dataframe.select(specific_cols)

    df = dataframe.with_columns(pl.col(column).forward_fill())
    df = df.drop_nulls(subset=[column])

    df = (df.sort("date").group_by("date").agg(pl.all().last()).sort("date"))

    print(df)

    df = df.with_columns(
        [
            pl.col("date").dt.year().alias("year"),
            pl.col("date").dt.month().alias("month"),
        ]
    )

    return df, md5


def compute_monthly_returns (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund :  Optional[str] = None,
        columns_fund : Optional[Dict] = None,

        year_month : List = ["year", "month"]
    ) :
    """
    Docstring for compute_monthly_returns
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    """
    fund = FUND_HV if fund is None else fund
    dataframe, _ = estimated_gross_performance(fund=fund, columns_fund=columns_fund) if dataframe is None else dataframe, md5

    columns_fund = NAV_FUNDS_COLUMNS if columns_fund is None else columns_fund
    column = columns_fund.get(fund)

    monthly = (

        dataframe
        .group_by(year_month)
        .agg(
            pl.count().alias("rows_in_month"),
            pl.col(column).first().alias("first_nav"),
            pl.col(column).last().alias("last_nav"),
        )
        .sort(year_month)

    )

    monthly = monthly.with_columns(pl.col("last_nav").shift(1).alias("prev_last_nav"))

    monthly = monthly.with_columns(

        pl.when(pl.col("prev_last_nav").is_not_null())
          .then(pl.col("prev_last_nav"))
          .otherwise(pl.col("first_nav"))
          .alias("start_nav")

    )

    valid_month = (

        (pl.col("rows_in_month") >= 2) |
        ((pl.col("rows_in_month") == 1) & pl.col("prev_last_nav").is_not_null())
   
    )

    monthly = monthly.with_columns(

        pl.when(valid_month)
          .then(((pl.col("last_nav") / pl.col("start_nav")) - 1.0) * 100.0)
          .otherwise(pl.lit(None))
          .alias("monthly_return")

    )

    result: Dict[int, Dict[int, float]] = {}

    for year, month, perf in monthly.select(year_month + ["monthly_return"]).iter_rows() :

        year_int = int(year)
        month_int = int(month)

        if perf is None :
            perf_value = math.nan
        
        else :
            perf_value = float(perf)

        result.setdefault(year_int, {})[month_int] = perf_value

    # Ensure all years appear in result
    for year in dataframe.select(pl.col(year_month[0])).unique().to_series().to_list() :
        result.setdefault(int(year), {})

    month_abbrs = [calendar.month_abbr[m] for m in range(1, 13)]
    rows = []

    for year, month_dict in result.items() :

        row = {"Year": year}
        
        for m, abbr in enumerate(month_abbrs, start=1) :
        
            value = month_dict.get(m, math.nan)  # missing month -> NaN
            row[abbr] = value
        
        rows.append(row)

    perf_df = pl.DataFrame(rows).sort("Year")
    print(perf_df)
    return perf_df, md5


def build_performance_dataframe (

        dataframe : pl.DataFrame,
        md5 : str,

        fund : Optional[str] = None,


    ) :
    """
    Docstring for build_performance_dataframe
    """
    fund = FUND_HV if fund is None else fund

    

    