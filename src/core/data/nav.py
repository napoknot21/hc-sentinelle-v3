from __future__ import annotations

import os
import re
import math
import hashlib
import calendar
import polars as pl
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str, str_to_date
#from src.core.data.volatility import compute_realized_vol_by_dates
from src.config.parameters import (
    FUND_HV, NAV_HISTORY_COLUMNS, NAV_HIST_NAME_DEFAULT, NAV_CUTOFF_DATE,
    NAV_ESTIMATE_HIST_NAME_DEFAULT, NAV_ESTIMATE_COLUMNS, NAV_ESTIMATE_RENAME_COLUMNS,
    NAV_FUNDS_COLUMNS, NAV_PORTFOLIO_REGEX, NAV_PORTFOLIO_COLUMNS, PERF_HARDCODED_VALUES,
    PERF_BOOKS_FUNS, PERF_ASSET_CLASSES_FUNDS, PERF_ALLOCATION_DATE, PERF_INITIAL_ALLOCATION
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
    excel_file_abs_path = get_nav_history_path_by_fund(fund, nav_fund_paths)

    schema_overrides = NAV_HISTORY_COLUMNS if schema_overrides is None else schema_overrides
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


def get_estimated_nav_df_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        agg_col : Optional[str] = None,

    ) :
    """
    Docstring for get_estimated_nav_by_date

    """
    fund = FUND_HV if fund is None else fund
    date = str_to_date(date)
    
    dataframe, md5 = read_history_nav_from_excel(fund) if dataframe is None else Tuple[dataframe, md5]

    df_filtered = dataframe.filter(pl.col("Date") == date)

    if df_filtered.is_empty() :

        latest_date = dataframe.select(pl.col("Date")).max().to_pandas().iloc[0, 0]
        df_filtered = dataframe.filter(pl.col("Date") == latest_date)

    aggregated_data = df_filtered.group_by("Date").agg(pl.col(agg_col).sum().alias(agg_col).cast(pl.Int128))

    return aggregated_data, md5
    

def gav_performance_normalized_base_100 (

        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fund : Optional[str] = None,

        rename_cols : Optional[Dict] = None,
        

    ) :
    """
    Docstring for gav_performance_normalized_base_100
    """

    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)

    fund = FUND_HV if fund is None else fund

    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols
    columns = list(rename_cols.values())

    dataframe, md5 = read_nav_estimate_by_fund(fund)
    rename_df , md5 = rename_nav_estimate_columns(dataframe, md5)

    df_filtered = rename_df.filter(
        
        (pl.col("date") >= pl.lit(start_date)) &
        (pl.col("date") <= pl.lit(end_date))
    
    )

    df_ffill = (

        df_filtered
        .sort("date")
        .with_columns(
            [pl.col(c).forward_fill() for c in columns]
        )
    )

    df_clean = df_ffill.drop_nulls(subset=columns)

    if df_clean.height == 0 :
        return df_clean, md5
    
    # Normalization
    df_norm = df_clean.with_columns(
        [
            (pl.col(c) / pl.col(c).first() * 100.0).alias(c)
            for c in columns
        ]
    )

    return df_norm, md5






def treat_string_nav_cols_df (
    
        _df : pl.DataFrame,
        md5_hash : Optional[str] = None,
        string_cols : Optional[List[str]] = None

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    string_cols = [col for col, dtype in NAV_HISTORY_COLUMNS.items() if dtype == pl.Utf8] if string_cols is None else string_cols

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


def get_nav_history_path_by_fund (
        
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


def get_nav_portfolio_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str | dt.datetime | dt.date] = None,

        nav_fund_paths : Optional[Dict] = None,
        regex : Optional[re.Pattern] = None,
        schema_overrides : Optional[Dict] = None,
        mode : str = "eq"

    ) :
    """
    Docstring for get_nav_bye_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fund: Description
    :type fund: Optional[str | dt.datetime | dt.date]
    :param nav_fund_paths: Description
    :type nav_fund_paths: Optional[Dict]
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    regex = NAV_PORTFOLIO_REGEX if regex is None else regex

    schema_overrides = NAV_PORTFOLIO_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    nav_fund_paths = NAV_PORTFOLIO_FUNDS_DIR_PATHS if nav_fund_paths is None else nav_fund_paths
    dir_abs_path = nav_fund_paths.get(fund)

    filename, date_find = find_most_recent_nav_by_date(date, fund, nav_fund_paths, regex, mode=mode)

    if filename is None :
        return None, None
    
    full_path = os.path.join(dir_abs_path, filename)

    dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides, specific_cols=specific_cols)

    return dataframe, md5, date_find # In this case ne return the date also bc Maybe the selected date is not the same as the found one


def compute_mv_change_by_dates (
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fund : Optional[str] = None,
        column : Optional[str] = "MV/NAV%",
        merge_on : str = "Portfolio Name",
    
    ) :
    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)

    start, md5_start, start_real_date = get_nav_portfolio_by_date(start_date, fund, mode="ge")
    end, md5_end, end_real_date= get_nav_portfolio_by_date(end_date, fund, mode="le")

    if start is None or end is None :

        print("[-] Error during reading files")
        return pl.DataFrame()

    merged = end.join(start, on=merge_on, how="inner", suffix="_start")

    merged = merged.filter(

        (pl.col(f"{column}_start").is_not_null()) & (pl.col(column).is_not_null()) &
        (pl.col(f"{column}_start") != 0) & (pl.col(column) != 0)

    )

    result = merged.select(
        [
            merge_on,
            (pl.col(column) - pl.col(f"{column}_start")).alias('MV NAV Change %')
        ]
    
    )

    return result, md5_start, md5_end, start_real_date, end_real_date


def find_most_recent_nav_by_date(
        
        date: Optional[str | dt.datetime | dt.date] = None,
        fund: Optional[str] = None,

        nav_fund_paths: Optional[Dict[str, str]] = None,
        regex: Optional[re.Pattern] = None,

        mode: str = "eq",  # "eq", "le", "ge"
    ) -> Tuple[Optional[str], Optional[str]]:
    """
    Find NAV file according to a target date and a search mode.

    :param date: Target date (string 'YYYY-MM-DD' or date/datetime).
    :param fund: Fund name.
    :param nav_fund_paths: Mapping fund -> directory path.
    :param regex: Compiled regex with groups: (date_str, hh, mm).
    :param mode: 
        - "eq": exact date only
        - "le": latest date <= target date
        - "ge": earliest date >= target date

    :return: (filename, chosen_date_str) or (None, None)
    """

    date_str_target = date_to_str(date)           # "YYYY-MM-DD"
    fund = FUND_HV if fund is None else fund
    nav_fund_paths = NAV_PORTFOLIO_FUNDS_DIR_PATHS if nav_fund_paths is None else nav_fund_paths
    dir_abs_path = nav_fund_paths.get(fund)

    if dir_abs_path is None:
        return None, None

    if regex is None:
        # À adapter à ton pattern réel
        # Exemple: r"^NAV_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})\.xlsx$"
        raise ValueError("regex must be provided")

    # Pour chaque date, on garde le *meilleur* fichier (heure + mtime)
    # best_per_date[date_str] = (hh, mm, mtime, filename)
    best_per_date: Dict[str, Tuple[int, int, float, str]] = {}

    with os.scandir(dir_abs_path) as it :

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

            key = (hh_i, mm_i, mtime)

            current = best_per_date.get(date_str)
            if current is None or key > current[:3]:
                # On stocke hh, mm, mtime + filename
                best_per_date[date_str] = (hh_i, mm_i, mtime, entry.name)

    if not best_per_date:
        return None, None

    # Si on a exactement la date cible, on la privilégie pour tous les modes
    if date_str_target in best_per_date:
        _, _, _, fname = best_per_date[date_str_target]
        return fname, date_str_target

    # Pas de fichier pour la date exacte -> on applique le "mode"
    all_dates = sorted(best_per_date.keys())  # tri lexical = tri chronologique

    if mode == "eq":
        # strict : rien trouvé à la date exacte
        return None, None

    elif mode == "le":
        # Dernière date <= date cible
        candidates = [d for d in all_dates if d <= date_str_target]
        if not candidates:
            return None, None
        chosen_date = candidates[-1]

    elif mode == "ge":
        # Première date >= date cible
        candidates = [d for d in all_dates if d >= date_str_target]
        if not candidates:
            return None, None
        chosen_date = candidates[0]

    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'eq', 'le' or 'ge'.")

    _, _, _, fname = best_per_date[chosen_date]
    return fname, chosen_date


def estimated_gross_performance (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund :  Optional[str] = None,
        columns_fund : Optional[Dict] = None,
    
    ) :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    dataframe, md5 = read_nav_estimate_by_fund(fund) if dataframe is None else (dataframe, md5)
    
    columns_fund = NAV_FUNDS_COLUMNS if columns_fund is None else columns_fund
    column = columns_fund.get(fund)

    df = dataframe.with_columns(pl.col(column).forward_fill())
    df = df.drop_nulls(subset=[column])

    df = (df.sort("date").group_by("date").agg(pl.all().last()).sort("date"))

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

        year_month : List = ["year", "month"],
        hardcoded : Optional[Dict] = None,
    ) :
    """
    Docstring for compute_monthly_returns
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    """
    fund = FUND_HV if fund is None else fund
    dataframe, md5 = estimated_gross_performance(fund=fund, columns_fund=columns_fund) if dataframe is None else (dataframe, md5)

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

    # Hardcoding a exceptional value
    hardcoded = PERF_HARDCODED_VALUES if hardcoded is None else hardcoded
    hardcoded_fund = hardcoded.get(fund)

    if hardcoded_fund is None :
        return perf_df, md5

    value = (-1.0) * float(hardcoded.get(fund).get("Value"))

    perf_df = perf_df.with_columns(

        pl
        .when(pl.col("Year") == int(hardcoded.get(fund).get("Year")))
        .then(pl.lit(value))
        .otherwise(pl.col(hardcoded.get(fund).get("Month")))
        .alias(hardcoded.get(fund).get("Month"))

    )
    
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


def portfolio_allocation_analysis (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        avoid_books_funds : Optional[Dict] = None,
        asset_class_funds : Optional[Dict[str, Dict[str, List]]] = None,

        initial_allocation : Optional[Dict] = None,
        threshold : Optional[str | dt.datetime | dt.date] = None,

    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    avoid_books_funds = PERF_BOOKS_FUNS if avoid_books_funds is None else avoid_books_funds
    asset_class_funds = PERF_ASSET_CLASSES_FUNDS if asset_class_funds is None else asset_class_funds

    initial_allocation = PERF_INITIAL_ALLOCATION if initial_allocation is None else initial_allocation
    threshold = str_to_date(PERF_ALLOCATION_DATE) if threshold is None else str_to_date(threshold)

    dataframe, md5, real_date = get_nav_portfolio_by_date(date, fund, mode="le") 

    asset_classes_book_names = asset_class_funds.get(fund) # Dict [str , List]

    init_alloc = {}

    for key, _ in asset_classes_book_names.items() :
        init_alloc[key] = initial_allocation.get(key)

    if (date < threshold) :
        asset_classes_book_names["Equity"] = asset_classes_book_names.get("Equity")[:1]

    filter_book = avoid_books_funds.get(fund)

    dataframe = dataframe.filter(pl.col("Portfolio Name") != filter_book)

    records = []
    for asset_class, books in asset_classes_book_names.items() :

        for book in books :
            records.append({"Portfolio Name": book, "Asset Class": asset_class})

    mapping_df = pl.DataFrame(records)
    dataframe = dataframe.join(mapping_df, on="Portfolio Name", how="left")

    # TODO : Look for other books that are not listed
    ptf_agg = (

        dataframe
        .group_by("Asset Class")
        .agg(
            [
                pl.col("MV").sum().alias("MV"),
            ]
        )

    )

    #ptf_agg = ptf_agg.drop_nulls("Asset Class")

    ptf_agg = ptf_agg.with_columns(

        pl.col("Asset Class")
        .replace(init_alloc)
        .alias("alloc")
        .cast(pl.Float64)
    
    )

    ptf_agg = ptf_agg.with_columns(
        [
            ((pl.col("MV") / pl.col("alloc") + 1) * 100).alias("Nav of Asset Class"),
            pl.col("MV").alias("Generated PNL of Asset Class"),
        ]
    )
    
    print(ptf_agg)

    return ptf_agg


    