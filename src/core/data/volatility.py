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

