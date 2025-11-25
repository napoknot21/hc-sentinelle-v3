from __future__ import annotations

import polars as pl
import streamlit as st
import datetime as dt

from typing import Optional

from src.utils.formatters import date_to_str, str_to_date

#from src.core.api.simm import *
from src.core.data.simm import get_simm_by_date, get_simm_history
from src.core.data.nav import read_history_nav_from_excel

from src.ui.components.text import center_h2
from src.ui.components.charts import simm_ctpy_im_vm_chart, simm_over_time_chart, total_nav_over_time_chart, im_mv_over_nav_with_rolling


def simm (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("SIMM")
    
    date_simm_bar_section(date, fundation)
    st.write('')

    im_mv_over_time_section(date, fundation)
    st.write('')

    total_nav_section(date, fundation)
    st.write('')

    im_mv_total_over_nav_section(date, fundation)
    
    return None


# ----------- SIMM Bar Chart -----------

# TODO  
def realized_var_cvar_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) :
    """
    
    """
    dataframe, md5 = get_simm_by_date(date, fundation)

    date = date_to_str(date)
    fig = simm_ctpy_im_vm_chart(dataframe, md5, date, "Counterparty", ("IM", "MV"))

    st.plotly_chart(fig, use_container_width=True)

    return None


def date_simm_bar_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) :
    """
    
    """
    dataframe, md5 = get_simm_by_date(date, fundation)

    date = date_to_str(date)
    fig = simm_ctpy_im_vm_chart(dataframe, md5, date, "Counterparty", ("IM", "MV"))

    st.plotly_chart(fig, use_container_width=True)
    
    return None


# ----------- IM and MV over time -----------

def im_mv_over_time_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """
    col1, col2 = st.columns(2)

    with col1 :
        im_over_time_section(date, fundation)

    with col2 :
        mv_over_time_section(date, fundation)

    return None


def im_over_time_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) :
    """
    
    """
    dataframe, md5 = get_simm_history(date, fundation)

    date = str_to_date(date)
    dataframe = dataframe.filter(pl.col("Date") <= date)

    date = date_to_str(date)
    fig = simm_over_time_chart(
    
        dataframe, md5,
        f"IM over time until {date} (ICE data)",
        date, "Counterparty", "IM"
    
    )

    st.plotly_chart(fig, use_container_width=True,)


def mv_over_time_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    dataframe, md5 = get_simm_history(date, fundation)

    date = str_to_date(date)
    dataframe = dataframe.filter(pl.col("Date") <= date)

    date = date_to_str(date)
    fig = simm_over_time_chart(
    
        dataframe, md5,
        f"MV over time until {date} (ICE data)",
        date, "Counterparty", "MV"
    
    )

    st.plotly_chart(fig, use_container_width=True,)


# ----------- Counterparty ICE / data (IM / MV) -----------

def total_im_mv_section () :
    """
    
    """


def total_im_across_ctpy () :
    """
    
    """


def total_mv_across_ctpy () :
    """
    
    """


# ----------- NAV over time -----------

def total_nav_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """
    dataframe, md5 = read_history_nav_from_excel(fundation)

    date = str_to_date(date)
    dataframe = dataframe.filter(pl.col("Date") <= date)

    nav_df = dataframe.group_by("Date").agg(pl.col("MV").sum().alias("NAV")).sort("Date")
    nav_df = nav_df.sort("Date")

    nav_df = _smooth_mv(nav_df)

    fig = total_nav_over_time_chart(nav_df, md5, date, fundation, f"Total NAV overt time until {date}")
    
    st.plotly_chart(fig)
    return None


def _smooth_mv (
        
        df: pl.DataFrame,
        pct_jump_threshold : float = 0.25
    
    ) -> pl.DataFrame:
    """
    Supprime les points où la variation relative dépasse pct_jump_threshold.
    Exemple: 0.25 -> écarte tout saut > 25%.
    """
    df = df.sort("Date").with_columns(
        (pl.col("NAV") / pl.col("NAV").shift(1) - 1).alias("pct_change")
    )

    # on garde les points "raisonnables"
    cleaned = df.filter(
        (pl.col("pct_change").abs() < pct_jump_threshold) | pl.col("pct_change").is_null()
    ).select(["Date", "NAV"])

    return cleaned


# ----------- IM & MV Total over NAV -----------

def im_mv_total_over_nav_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """

    col1, col2 = st.columns(2)

    with col1 :
        im_over_nav_section(date, fundation)

    with col2 :
        mv_over_nav_section(date, fundation)

    return None


def im_over_nav_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        column : str = "IM"

    ) :
    """
    
    """
    dataframe, md1, md2 = _im_or_mv_over_nav(date, fundation, column)
    
    fig = im_mv_over_nav_with_rolling(dataframe, md1, md2, column)
    st.plotly_chart(fig)

    return None


def mv_over_nav_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        column : Optional[str] = "MV"

    ) :
    """
    
    """
    dataframe, md1, md2 = _im_or_mv_over_nav(date, fundation, column)

    fig = im_mv_over_nav_with_rolling(dataframe, md1, md2, column)
    st.plotly_chart(fig)

    return None


def _im_or_mv_over_nav (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        column : Optional[str] = None,
        
    ): 
    """
    """
    df_nav, md5_nav = read_history_nav_from_excel(fundation)
    df, md5 = get_simm_history(date, fundation)

    date = str_to_date(date)
    df_nav = df_nav.filter(pl.col("Date") <= date)
    df = df.filter(pl.col("Date") <= date)

    nav_df = (
        df_nav
        .group_by("Date")
        .agg(pl.col("MV").sum().alias("NAV"))
        .sort("Date")
    )

    # IM par jour (somme)
    df = (
        df
        .group_by("Date")
        .agg(pl.col(column).sum().alias(column))
        .sort("Date")
    )

    merged_df = (

        nav_df
        .join(df, on="Date", how="inner")
        .with_columns((pl.col(column) / pl.col("NAV") * 100).alias(f"{column}/NAV %"))
        .sort("Date")
    
    )

    print(merged_df)

    return merged_df, md5_nav, md5

