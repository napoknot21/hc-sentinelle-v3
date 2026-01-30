from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt
import numpy as np

from typing import Optional, List, Dict, Tuple

from src.core.data.nav import read_nav_estimate_by_fund

from src.config.parameters import VOL_REALIZED_FUNDS_COLS, FUND_HV
from src.utils.formatters import str_to_date


def read_realized_vol_by_dates (
        
        fund : Optional[str] = None,

        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        funds_cols : Optional[Dict] = None,

    ) :
    """

    """

    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)

    fund = FUND_HV if fund is None else fund
    funds_cols = VOL_REALIZED_FUNDS_COLS if funds_cols is None else funds_cols

    column = funds_cols.get(fund)
    dataframe, md5 = read_nav_estimate_by_fund(fund)

    specific_cols = [column] + ["date"]
    df_filtered = dataframe.select(specific_cols)

    df_sorted = df_filtered.sort("date")

    df = df_sorted.filter((pl.col("date") >= pl.lit(start_date)) & (pl.col("date") <= pl.lit(end_date)))

    return df, md5


def compute_realized_vol_by_dates (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund : Optional[str] = None,

        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        funds_cols : Optional[Dict] = None,

    ) :
    """
    
    """
    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)
    
    fund = FUND_HV if fund is None else fund
    funds_cols = VOL_REALIZED_FUNDS_COLS if funds_cols is None else funds_cols

    dataframe, md5 = read_realized_vol_by_dates(fund, start_date, end_date) if dataframe is None else (dataframe, md5)
    column = funds_cols.get(fund)

    dataframe = dataframe.with_columns(
        pl.when(pl.col(column).is_nan())
          .then(None)
          .otherwise(pl.col(column))
          .alias(column)
    )

    df = dataframe.sort("date").with_columns(pl.col("date").dt.date().alias("day_only"))
    df = df.group_by("day_only")
    df = df.tail(1).sort("day_only").rename({"day_only": "Date"})
    
    df = df.with_columns(pl.when(pl.col(column).is_nan()).then(None).otherwise(pl.col(column)).alias(column))
    df = df.with_columns(pl.col(column).fill_null(strategy="forward"))

    df = df.filter(pl.col(column).is_not_null())

    df = df.select(["Date", column])

    return df


def compute_annualized_realized_vol (
    
        dataframe : Optional[pl.DataFrame] = None,
        fund : Optional[str] = None,

        funds_cols : Optional[Dict] = None,

    ) :
    """
    Docstring for compute_annualized_realized_vol
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param column: Description
    :type column: Optional[str]
    """
    if dataframe is None :
        return 0.0
    
    fund = FUND_HV if fund is None else fund
    funds_cols = VOL_REALIZED_FUNDS_COLS if funds_cols is None else funds_cols

    column = funds_cols.get(fund)

    df = dataframe.sort("Date")

    df = df.with_columns(
        (pl.col(column) / pl.col(column).shift(1)).alias("ratio"),
    )

    df = df.with_columns(
        pl.when(pl.col("ratio").is_null())
        .then(None)
        .otherwise(pl.col("ratio").log())
        .alias("daily_return")
    )

    df = df.filter(pl.col("daily_return").is_not_null())

    if df.height == 0:
        return 0.0

    # tandard deviation of daily returns ----
    daily_vol = df.select(pl.col("daily_return").std()).item()

    if daily_vol is None :
        return 0.0
    
    # Annualize
    trading_days = 252
    annualized_vol = daily_vol * np.sqrt(trading_days) * 100

    return round(float(annualized_vol), 2)


def calculate_rv_estimated_perf (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund : Optional[str] = None,
        columns : Optional[List[str]] = None,

        annualize : bool = True,
        min_months : int = 2

    ) :
    """
    Docstring for calculate_total_n_rv_estimated_perf
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    """
    fund = FUND_HV if fund is None else fund

    columns = [c for c in dataframe.columns if c != "Year"] if columns is None else columns

    # keep only month columns
    columns = [c for c in columns if c not in ["Total", "RV"]]

    dataframe = dataframe.with_columns(


        pl.concat_list(

            [
                pl.when(pl.col(c).is_nan())
                  .then(pl.lit(None))
                  .otherwise(pl.col(c))
                for c in columns
            ]

        )
        .list.eval(pl.element().drop_nulls())
        .alias("rv_values")

    )

    rv_expr = pl.col("rv_values").list.std()

    if annualize :
        rv_expr = rv_expr * (12.0 ** 0.5)

    dataframe = dataframe.with_columns(

        pl.when(pl.col("rv_values").list.len() >= min_months)
          .then(rv_expr)
          .otherwise(pl.lit(None))
          .alias("RV")

    )

    dataframe = dataframe.drop("rv_values")

    return dataframe, md5
    """
    years = dataframe.get_column("Year").to_list()
    rv_map: dict[int, float] = {}
    
    for year in years :

        start_date = str(f"{year}-01-01")
        end_date = str(f"{year}-12-31")

        vol_df = compute_realized_vol_by_dates(fund=fund, start_date=start_date, end_date=end_date)
        rv_value = compute_annualized_realized_vol(vol_df, fund)

        if rv_value is None :
            rv_map[year] = None

        else :
            rv_map[year] = rv_value

    dataframe = dataframe.with_columns(

        pl.col("Year")
        .cast(pl.Float64)
        .replace(rv_map)       # map Year -> RV
        .alias("RV")
    
    )

    return dataframe, md5
    """



