from __future__ import annotations

import calendar
import polars as pl
import datetime as dt
import streamlit as st

from typing import Dict, List, Optional, Dict
# from dateutil.relativedelta import relativedelta

from src.ui.components.selector import date_selector
from src.ui.components.text import center_h2, left_h5, left_h3
from src.ui.components.charts import nav_estimate_performance_graph,mv_change_peformance_chart

from src.config.parameters import NAV_ESTIMATE_RENAME_COLUMNS, PERF_DEFAULT_DATE, PERF_ASSET_CLASSES_FUNDS
from src.utils.formatters import (
    date_to_str, str_to_date, shift_months, monday_of_week, format_numeric_columns_to_string, colorize_dataframe_positive_negatif_vals

)
from src.core.data.nav import (
    read_nav_estimate_by_fund, rename_nav_estimate_columns, read_history_nav_from_excel,
    estimated_gross_performance, compute_monthly_returns, compute_mv_change_by_dates,
    portfolio_allocation_analysis, get_estimated_nav_df_by_date, gav_performance_normalized_base_100,
    calculate_total_n_rv_estimated_perf
)
from src.core.data.subred import *
from src.core.data.volatility import read_realized_vol_by_dates, compute_realized_vol_by_dates, compute_annualized_realized_vol
from src.core.api.subred import get_subred_by_date

# Main function

def performance (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    # Start Date and End Date variables
    if "start_date_perf" not in st.session_state :
        st.session_state.start_date_perf = str_to_date(PERF_DEFAULT_DATE)
        
    if "end_date_perf" not in st.session_state :
        st.session_state.end_date_perf = dt.date.today()
    
    
    center_h2("Performances")
    st.write('')

    estimated_gross_perf_section(date, fundation)
    st.write('')
    
    volatility_aum_n_nav_section(date, fundation)
    st.write('')
    
    start_date, end_date = date_selectors_section()

    charts_performance_section( fundation, start_date, end_date)
    contribution_charts_section(date, fundation, start_date, end_date)

    return None


# ----------- Gross Estimated Perf Section -----------

def estimated_gross_perf_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
    
    ) -> None :
    """
    
    """
    left_h3("Estimated Gross Performance (in %)")

    result, md5 = estimated_gross_performance(fund=fundation)
    dataframe, md5 = compute_monthly_returns(result, md5, fundation)

    month_cols = [c for c in dataframe.columns if c not in ["Year"]]
    dataframe, md5 = calculate_total_n_rv_estimated_perf(dataframe, md5, fundation, month_cols)

    years = dataframe.get_column("Year").to_list()
    rv_map: dict[int, float] = {}
    
    for year in years :

        start_date = str(f"{year}-01-01")
        end_date = str(f"{year}-12-31")

        vol_df = compute_realized_vol_by_dates(fund=fundation, start_date=start_date, end_date=end_date)
        rv_value = compute_annualized_realized_vol(vol_df, fundation)
        print(rv_value)
        # Si ta fonction peut renvoyer None, tu gères ça ici
        if rv_value is None:
            rv_map[year] = None
        else:
            rv_map[year] = (rv_value)

    dataframe = dataframe.with_columns(
        pl.col("Year")
        .replace(rv_map)       # map Year -> RV
        .alias("RV")
        .cast(pl.Float64)      # juste pour être sûr que c’est bien numérique
    )
    print(dataframe)
    month_cols = month_cols + ["Total", "RV"]
    dataframe = format_numeric_columns_to_string(dataframe, month_cols)
    dataframe  = colorize_dataframe_positive_negatif_vals(dataframe, month_cols)
    
    st.dataframe(dataframe)
    
    return None


# ----------- AUM & NAV -----------

def volatility_aum_n_nav_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

    ) -> None :

    """
    
    """
    #left_h5("Most recent AUM and Estimated NAV")
    col1, col2= st.columns(2)

    with col1 :
        total_aum_section(date, fundation)

    with col2 :
        daily_nav_section(date, fundation)

    return None


def total_aum_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """
    date = date_to_str(date)
    aum_dict = read_aum_from_cache(date)
    
    if aum_dict is None :

        aum_dict = get_subred_by_date(date)

    aum = aum_dict.get(fundation, None)

    if aum is None :

        st.metric(f"No data AUM available", "")
        return 

    currency = aum.get("currency")
    amount = aum.get("amount")

    save_aum_to_cache(aum_dict, date)
    st.metric(f"Total AUM at {date}", f"{amount} {currency}")
    
    return None


def daily_nav_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        agg_col : Optional[str] = "MV"

    ) :
    """
    
    """
    date = str_to_date(date)
    dataframe, _ = get_estimated_nav_df_by_date(date, fundation, agg_col=agg_col)
    
    aggregated_data = format_numeric_columns_to_string(dataframe)

    real_date = aggregated_data.get_column("Date")[0]
    nav_estimated = (aggregated_data.get_column(agg_col)[0])[:-3] #TODO : update the format numerica columns 

    st.metric(f"Estimated NAV at {real_date}", nav_estimated + " EUR")

    return None


# ----------- Date selector section -----------

def date_selectors_section () :
    """
    
    """
    col1, col2 = st.columns(2)

    with col1 :
        performance_date_quick_selectors(end_ref_date=st.session_state.end_date_perf)
    
    with col2 :
        start_date, end_date = performance_date_manual_selectors()

    return start_date, end_date


def performance_date_manual_selectors () :
    """
    
    """
    left_h5("Manual Date Selector")
    col1 , col2 = st.columns(2)

    with col1 :

        start_default = st.session_state.start_date_perf
        start_val = date_selector("Start Date", default_value=start_default, key="start_date_perf")
    
    with col2 :

        end_default = st.session_state.end_date_perf
        end_val = date_selector("End Date", default_value=end_default, key="end_date_perf")
    
    # Parse locally
    start_date = str_to_date(start_val)
    end_date   = str_to_date(end_val)

    return start_date, end_date


def performance_date_quick_selectors (
        
        start_default_date : Optional[str | dt.date | dt.datetime] = None,
        end_ref_date : Optional[str | dt.date | dt.datetime] = None
    
    ) :
    """
    
    """
    start_default_date = PERF_DEFAULT_DATE if start_default_date is None else start_default_date
    end_ref = str_to_date(end_ref_date) if end_ref_date is not None else dt.date.today()
    start_default = str_to_date(start_default_date)

    left_h5("Quick Date Selector")
    st.write('')

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        
        if st.button("ALL", key="perf_button_all") :

            st.session_state.start_date_perf = start_default
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col2 :

        if st.button("1YTD", key="perf_ytd_button_year") :

            st.session_state.start_date_perf = dt.date(end_ref.year, 1, 1)
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col3 :

        if st.button("6MTD", key="perf_ytd_button_6_months"):
            
            # rolling 6 months inclusive
            st.session_state.start_date_perf = shift_months(end_ref, -6) + dt.timedelta(days=1)
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col4 :

        if st.button("1MTD", key="perf_ytd_button_1_month"):
        
            st.session_state.start_date_perf = dt.date(end_ref.year, end_ref.month, 1)
            st.session_state.end_date_perf = end_ref
        
            st.rerun()

    with col5:
        
        if st.button("1WTD", key="perf_ytd_button_1_week"):
        
            st.session_state.start_date_perf = monday_of_week(end_ref)
            st.session_state.end_date_perf = end_ref
        
            st.rerun()

    return st.session_state.start_date_perf, st.session_state.end_date_perf


# ----------- Charts Perf Section -----------

def charts_performance_section (
    
        fundation : Optional[str] = None,

        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None
    
    ) :
    """
    
    """
    performance_charts_section(start_date, end_date, fundation)

    st.write('')
    anualised_volatility_section(fundation, start_date, end_date)
    st.write('')

    realized_volatilty_chart_section(start_date, end_date, fundation)

    return None


def performance_charts_section (
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fundation : Optional[str] = None,
        rename_cols : Optional[Dict] = None,
        
    ) :
    """
    
    """
    left_h5(f"{fundation} Performance between {start_date} and {end_date}")

    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)

    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols
    dataframe, md5 = gav_performance_normalized_base_100(start_date, end_date, fundation)

    fig = nav_estimate_performance_graph(
        dataframe, md5, fundation, start_date, end_date, list(rename_cols.values()), "date"
    )

    st.plotly_chart(fig)

    return None


def anualised_volatility_section (
        
        fundation : Optional[str] = None,
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,


    ) -> None :
    """
    
    """

    df, md5 = read_realized_vol_by_dates(fundation, start_date, end_date)
    dataframe = compute_realized_vol_by_dates(df, md5, fundation, start_date, end_date)
    vol = compute_annualized_realized_vol(dataframe, fundation)

    st.metric(f"{fundation} Realized Volatility between {start_date} and {end_date}", f"{vol}%")

    return None


def realized_volatilty_chart_section (
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fundation : Optional[str] = None,
        rename_cols : Optional[Dict] = None,

        window : int = 252,
        annual_factor : int = (252 ** 0.5) * 100,

    ) :
    """
    
    """
    left_h5(f"{fundation} realized Volatility (%) between {start_date} and {end_date}")

    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols
    columns = list(rename_cols.values())

    dataframe, md5 = read_nav_estimate_by_fund(fundation)
    rename_df , md5 = rename_nav_estimate_columns(dataframe, md5)


    df_na = rename_df.drop_nulls(subset=columns)
    df = df_na.sort("date")

    for column in columns :
        
        df = df.with_columns(
            [
                pl.col(column).pct_change().alias(f"{column}_returns")
            ]
        )

    annualization = (window ** 0.5) * 100

    for column in columns :

        df = df.with_columns(
            [
                pl.col(f"{column}_returns")
                .rolling_std(window_size=window, min_periods=window)
                .mul(annualization)
                .alias(f"VOL {column}"),
            ]
        )

        print(df)
    
    specific_cols = [f"VOL {column}" for column in columns]

    fig = nav_estimate_performance_graph(
        df, md5, fundation, start_date, end_date, specific_cols, "date"
    )

    st.plotly_chart(fig)

    return None


# ----------- Contribution section -----------

def contribution_charts_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        start_date : Optional[str] = None,
        end_date : Optional[str] = None,

    ) :
    """
    Docstring for contribution_charts_section
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fundation: Description
    :type fundation: Optional[str]
    :param start_date: Description
    :type start_date: Optional[str]
    :param end_date: Description
    :type end_date: Optional[str]
    """
    date = str_to_date(date)

    mv_change_section(fundation, start_date, end_date)
    portfolio_allocation_section(date, fundation)

    return None


def mv_change_section (
        
        fundation : Optional[str] = None,

        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,


    ) :
    """
    Docstring for mv_change_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    :param start_date: Description
    :type start_date: Optional[str | dt.datetime | dt.date]
    :param end_date: Description
    :type end_date: Optional[str | dt.datetime | dt.date]
    """
    start_date = date_to_str(start_date)
    end_date = date_to_str(end_date)

    dataframe, md5_1, md5_2 = compute_mv_change_by_dates(start_date, end_date, fundation)
    fig = mv_change_peformance_chart(dataframe, md5_1, md5_2)
    
    left_h5(f"MV % Change per Book — {fundation} from {start_date} to {end_date}")
    st.plotly_chart(fig)

    return None


def portfolio_allocation_section (
        
        date : Optional[str] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """
    #print(PERF_ASSET_CLASSES_FUNDS)

    datframe = portfolio_allocation_analysis(date, fundation)
    st.dataframe(datframe)

    return None


