from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt

from typing import Optional, List, Dict

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

        fund : Optional[str] = None,

        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        funds_cols : Optional[Dict] = None,

    ) :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    dataframe = read_realized_vol_by_dates(fund, start_date, end_date) if dataframe is None else dataframe

    return None


