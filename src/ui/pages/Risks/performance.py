from __future__ import annotations

import polars as pl
import datetime as dt
import streamlit as st

from typing import Dict, List, Optional, Dict

from src.ui.components.selector import date_selector
from src.ui.components.text import center_h2, left_h5
from src.ui.components.charts import nav_estimate_performance_graph

from src.config.parameters import NAV_ESTIMATE_RENAME_COLUMNS
from src.core.data.nav import read_nav_estimate_by_fund, rename_nav_estimate_columns


def performance (date : Optional[str | dt.datetime | dt.date] = None, fundation : Optional[str] = None) :
    """
    
    """
    center_h2("Performances")
    st.write('')
    
    nav_estimate_section(fundation)

    return None



def nav_estimate_section (fundation : Optional[str] = None) :
    """
    
    """

    start_date, end_date = performance_date_selectors()


    left_h5(f"{fundation} Performance between {start_date} and {end_date}")
    st.plotly_chart(performance_charts_section(start_date, end_date, fundation))

    st.write('')

    left_h5(f"{fundation} Realized Volatility between {start_date} and {end_date}")
    st.plotly_chart(performance_charts_section(start_date, end_date, fundation))


def performance_date_selectors () :
    """
    
    """
    #st.set_page_config(layout="centered")
    col1 , col2 = st.columns(2)

    with col1 :
        start = dt.date(dt.datetime.now().date().year, 1, 1)
        start_date = date_selector("Dtart Date", type = start, key="start_date_perf")
    
    with col2 :
        end_date = date_selector("End Date", key="end_date_perf")
    
    return start_date, end_date


def performance_charts_section (
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fundation : Optional[str] = None,
        rename_cols : Optional[Dict] = None,
        
    ) :
    """
    
    """
    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols
    columns = list(rename_cols.values())

    dataframe, md5 = read_nav_estimate_by_fund(fundation)
    rename_df , md5 = rename_nav_estimate_columns(dataframe, md5)

    end_date = dt.datetime.now().date() if end_date is None else end_date
    start_date = dt.date(end_date.year, 1, 1) if start_date is None else start_date

    df_filterd = rename_df.filter(
        
        (pl.col("date") >= pl.lit(start_date)) &
        (pl.col("date") <= pl.lit(end_date))
    
    )

    df_na = df_filterd.drop_nulls(subset=columns)

    fig = nav_estimate_performance_graph(
        df_na, md5, fundation, start_date, end_date, columns, "date"
    )

    return fig


def realized_volatilty_chart_section (
        

    ) :
    return None
