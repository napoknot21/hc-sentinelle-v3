from __future__ import annotations

import polars as pl
import streamlit as st
import datetime as dt

from typing import Optional

from src.utils.formatters import date_to_str, str_to_date

from src.core.api.simm import fetch_raw_simm_data_by_date, convert_raw_simm_to_dataframe
from src.core.data.simm import (
    rename_ancien_simm_counterparties, get_simm_by_date_from_history, get_simm_all_history,
    update_simm_history
)
from src.core.data.nav import read_history_nav_from_excel

from src.ui.components.text import center_h2
from src.ui.components.charts import simm_ctpy_im_vm_chart, simm_over_time_chart, total_nav_over_time_chart, im_mv_over_nav_with_rolling


def _get_simm_display_date (
        dataframe : Optional[pl.DataFrame] = None,
        selected_date : Optional[str | dt.date | dt.datetime] = None
    ) -> str :
    """
    Display the actual SIMM date being shown when we fall back to cached data.
    """
    display_date = date_to_str(selected_date)

    if dataframe is None or dataframe.height == 0 or "Date" not in dataframe.columns :
        return display_date

    latest_date = dataframe.select(pl.col("Date").max()).item()
    return date_to_str(latest_date)


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
    
    return None


def date_simm_bar_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """
    

    dataframe, md5 = get_simm_all_history(fundation)
    df_date, md5_date = get_simm_by_date_from_history(date, dataframe, md5)
    
    if df_date is None or df_date.is_empty() :
        
        list = fetch_raw_simm_data_by_date(date, fundation)
        df_date, md5_date = convert_raw_simm_to_dataframe(date, list)

        if df_date is not None and not df_date.is_empty() :
            
            updated = update_simm_history(df_date, dataframe, md5)
            st.info("SIMM history sucessfully update" if updated else None)

    fig = simm_ctpy_im_vm_chart(df_date, md5_date, date, "Counterparty", ("IM", "MV"))

    if fig is None :
    
        st.warning(f"No SIMM data available for {date} and fund {fundation}.")
        return 
    
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
    dataframe, md5 = get_simm_all_history(fundation)

    date = str_to_date(date)
    dataframe = dataframe.filter(pl.col("Date") <= date)

    date = date_to_str(date)
    dataframe = rename_ancien_simm_counterparties(dataframe)

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
    dataframe, md5 = get_simm_all_history(fundation)

    date = str_to_date(date)
    dataframe = dataframe.filter(pl.col("Date") <= date)

    date = date_to_str(date)
    dataframe = rename_ancien_simm_counterparties(dataframe)

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
    Supprime les points oÃƒÆ’Ã‚Â¹ la variation relative dÃƒÆ’Ã‚Â©passe pct_jump_threshold.
    Exemple: 0.25 -> ÃƒÆ’Ã‚Â©carte tout saut > 25%.
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
    df, md5 = get_simm_all_history(fundation)

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


