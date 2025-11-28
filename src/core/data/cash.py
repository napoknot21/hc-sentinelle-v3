from __future__ import annotations

import os
import json
import hashlib
import datetime as dt
import polars as pl

from typing import Optional, Dict, Tuple

from src.config.paths import CASH_FUNDS_FILE_PATHS, COLLATERAL_FUNDS_FILE_PATHS, CASH_UPDATER_FX_VALUES_PATH
from src.config.parameters import CASH_COLUMNS, COLLATERAL_COLUMNS

from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import date_to_str, str_to_date

# --------- Cash ----------

def load_all_cash (
        
        fundation : str,

        schema_override : Optional[Dict] =  None,
        dir_dict_fund : Optional[Dict[str, str]] = None
        
    ) : 
    """
    
    """
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


def aggregate_n_groupby (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        target_date : Optional[str | dt.date | dt.datetime] = None,

        group_by_columns : Optional[Tuple] = None,
        aggregate_column : Optional[str] = None,

    ) -> Optional[pl.DataFrame] :
    """
    
    """
    target_date = dataframe.select(pl.col("Date").max()).to_dict()["Date"][0] if target_date is None else str_to_date(target_date)

    print(f"\n[*] Filtering by date: {target_date}")

    # Step 2: Filter the DataFrame by the target_date
    dataframe_dates = dataframe.filter(pl.col("Date") == target_date)

    if dataframe_dates.is_empty() :

        dates_series = (
            dataframe
            .select(pl.col("Date").unique().sort())
            .to_series()
        )

        # garder seulement les dates <= target_date
        prev_dates = dates_series.filter(dates_series <= target_date)

        if len(prev_dates) == 0:
            print("[!] No previous date available in dataframe.")
            return None, md5

        closest_date = prev_dates.max()
        print(f"[+] Using closest previous date: {closest_date}")

        dataframe_dates = dataframe.filter(pl.col("Date") == closest_date)

    # Step 3: Group by the specified columns and 'Currency'
    grouped_df = dataframe_dates.group_by(list(group_by_columns) + ["Currency"]).agg(
        pl.col(aggregate_column).sum().alias(aggregate_column)  # Sum the "Amount in CCY" for each currency
    )
    
    # Pivot the DataFrame so that each currency becomes a column
    pivot_df = grouped_df.pivot(

        values=aggregate_column,   # The values to aggregate (sum of "Total")
        index=list(group_by_columns),  # Grouping by "Bank" and "Type"
        columns="Currency"   # Pivoting by "Currency"
    
    )

    # Step 3: Fill missing values (i.e., currencies not present) with 0
    pivot_df = pivot_df.fill_null(0.0)
    
    return pivot_df, md5


def pivot_currency_historic (
    
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        tuples : Optional[Tuple[str, str]] = ("Bank", "Type"),
        x_axis : Optional[str] = "Date",
        selected_currency : str = "USD"
    
    ):
    """
    Pivot the data to show the historical value of the selected currency, grouped by Bank and Type.
    - Keep all available dates.
    - If the currency doesn't exist for a given Bank-Type-Date combination, set it to 0.

    Args:
    - df (pl.DataFrame): The Polars DataFrame containing the cash data.
    - selected_currency (str): The currency to focus on.

    Returns:
    - pl.DataFrame: The pivoted DataFrame for the selected currency.
    """
    # Filter the DataFrame to select only rows with the selected currency
    df_filtered = dataframe.filter(pl.col("Currency") == selected_currency)


    # Group by Bank, Type, and Date, and sum the Amount in EUR for the selected currency
    df_grouped = df_filtered.group_by(["Date", "Currency"] + list(tuples)).agg(
        pl.sum("Amount in CCY").alias(f"{selected_currency}_Amount")

    )
    print(df_grouped)

    # Pivot the DataFrame so that Date, Bank, and Type are the indexes
    # The selected currency will be the column with the aggregated amount
    df_pivoted = df_grouped.pivot(

        values=f"{selected_currency}_Amount",
        index=["Date"] + list(tuples),
        columns="Currency"
    
    )
    print(df_pivoted)

    # Fill any missing values with 0 (for combinations with no data in the selected currency)
    df_pivoted = df_pivoted.fill_null(0.0)

    return df_pivoted, md5


# --------- Collateral ----------

def load_all_collateral (
        
        fundation : str,

        schema_override : Optional[Dict] =  None,
        dir_dict_fund : Optional[Dict[str, str]] = None
        
    ) : 
    """
    
    """
    schema_override = COLLATERAL_COLUMNS if schema_override is None else schema_override
    columns = list(schema_override.keys())

    dir_dict_fund = COLLATERAL_FUNDS_FILE_PATHS if dir_dict_fund is None else dir_dict_fund

    filename = get_collateral_file_per_fundation(fundation, dir_dict_fund)

    if filename is None :
        return None, None
    
    dataframe, md5 = load_excel_to_dataframe(filename, specific_cols=columns, schema_overrides=schema_override, cast_num=False)

    return dataframe, md5


def load_collateral_by_date (
    
        date : Optional[str | dt.date | dt.datetime],
        fundation : str,

        schema_override : Optional[Dict] =  None
    
    ) :
    """
    
    """
    date = str_to_date(date)

    schema_override = COLLATERAL_COLUMNS if schema_override is None else schema_override
    columns = list(schema_override.keys())

    filename = get_collateral_file_per_fundation(fundation)

    if filename is None :
        return None, None
    
    dataframe, md5 = load_excel_to_dataframe(filename, specific_cols=columns, schema_overrides=schema_override, cast_num=False)

    df_date = dataframe.filter(pl.col("Date") == date)

    return df_date, md5


# --------- FX Values ---------

def load_cache_fx_values (
        
        file_abs_path : Optional[str] = None
        
    ) :
    """
    
    """
    file_abs_path = CASH_UPDATER_FX_VALUES_PATH if file_abs_path is None else file_abs_path

    if not os.path.exists(file_abs_path) :

        log("[-] The cache file does not exists. Using API...", "error")
        return None

    with open(file_abs_path, "r", encoding="utf-8") as f :

        try :

            log("[*] Loading FX values from Cash-updater")
            return json.load(f)
        
        except json.JSONDecodeError :
            
            log("[-] Error During reading FX values from cache", "error")
            return None


# --------- Collateral Graphs ---------




# --------- Auxiliar ---------

def get_cash_file_per_fundation (fundation : str, dir_dict_fund : Optional[Dict[str, str]] = None) -> Optional[str] :
    """
    
    """
    dir_dict_fund = CASH_FUNDS_FILE_PATHS if dir_dict_fund is None else dir_dict_fund

    filename = dir_dict_fund.get(fundation)

    if filename is None or not os.path.exists(filename) :
        return None
    
    return filename


def get_collateral_file_per_fundation (fundation : str, dir_dict_fund : Optional[Dict[str, str]] = None) -> Optional[str] :
    """
    
    """
    dir_dict_fund = COLLATERAL_FUNDS_FILE_PATHS if dir_dict_fund is None else dir_dict_fund

    filename = dir_dict_fund.get(fundation)

    if filename is None or not os.path.exists(filename) :
        return None
    
    return filename
