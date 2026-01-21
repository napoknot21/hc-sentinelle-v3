from __future__ import annotations

import calendar
import polars as pl
import datetime as dt
import streamlit as st

from st_aggrid import AgGrid, GridOptionsBuilder

from typing import Dict, List, Optional, Dict

from src.config.parameters import (
    NAV_ESTIMATE_RENAME_COLUMNS, PERF_DEFAULT_DATE, PERF_ASSET_CLASSES_FUNDS,
    SUBRED_BOOK_HV, AGGREGATED_POSITIONS_COLUMNS
)

from src.ui.components.selector import date_selector
from src.ui.components.text import center_h2, left_h5, left_h3
from src.ui.components.charts import nav_estimate_performance_graph,mv_change_peformance_chart
from src.ui.components.tables import show_aum_details_table

from src.utils.dates import monday_of_week, previous_business_day, get_qtd_from_date, get_mtd_start
from src.utils.formatters import (
    date_to_str, str_to_date, format_numeric_columns_to_string, colorize_dataframe_positive_negatif_vals
)

from src.core.api.subred import get_subred_by_date, fetch_subred_by_date
from src.core.data.subred import *
from src.core.data.nav import (
    read_nav_estimate_by_fund, rename_nav_estimate_columns, estimated_gross_performance,
    compute_monthly_returns, compute_mv_change_by_dates, portfolio_allocation_analysis,
    get_estimated_nav_df_by_date, gav_performance_normalized_base_100
)
from src.core.data.volatility import (
    read_realized_vol_by_dates, compute_realized_vol_by_dates, compute_annualized_realized_vol,
    calculate_total_n_rv_estimated_perf
)
from src.core.data.positions import (
    read_db_gross_data_by_date, asset_class_cascade_by_date
)



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
    date = previous_business_day(date)

    estimated_gross_perf_section(date, fundation)
    st.write('')
    
    volatility_aum_n_nav_section(date, fundation)
    st.write('')

    start_date, end_date = date_selectors_section()

    charts_performance_section(fundation, start_date, end_date)
    contribution_charts_section(date, fundation, start_date, end_date)
    aum_details_section(date)

    asset_class_aggregated_positions_section(date, fundation)

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
 
    month_cols = month_cols + ["Total", "RV"]
    dataframe = format_numeric_columns_to_string(dataframe, month_cols)

    styler  = colorize_dataframe_positive_negatif_vals(dataframe, month_cols)

    st.dataframe(styler)
    
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

        dataframe, md5 = read_detailed_aum_from_cache()

        if dataframe is None:
            dataframe , md5 = fetch_subred_by_date(date)

        aum_dict = get_subred_by_date(date, dataframe, md5)
        
        save_aum_to_cache(aum_dict, date)
        save_raw_aum_to_cache(dataframe, date)

    aum = aum_dict.get(fundation, None)

    if aum is None :

        st.metric(f"No data AUM available", "")
        return 

    currency = aum.get("currency")
    amount = aum.get("amount")

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
        #print(start_val)
    
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

        if st.button("YTD", key="perf_ytd_button_year") :

            start_raw = dt.date(end_ref.year-1, 12, 31)
            start = previous_business_day(start_raw)

            st.session_state.start_date_perf = start
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col3 :

        if st.button("QTD", key="perf_ytd_button_quarter"):

            start_raw = get_qtd_from_date(end_ref)
            start = previous_business_day(start_raw)

            st.session_state.start_date_perf = start
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col4 :

        if st.button("MTD", key="perf_ytd_button_1_month"):
            
            start_raw = get_mtd_start(end_ref)
            start = previous_business_day(start_raw)

            st.session_state.start_date_perf = start
            st.session_state.end_date_perf = end_ref
        
            st.rerun()

    with col5:
        
        if st.button("WTD", key="perf_ytd_button_1_week"):
        
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

    dataframe, md5_1, md5_2, real_start, real_end = compute_mv_change_by_dates(start_date, end_date, fundation)
    fig = mv_change_peformance_chart(dataframe, md5_1, md5_2)
    
    left_h5(f"MV % Change per Book — {fundation} from {real_start} to {real_end}")
    st.plotly_chart(fig)

    return None


def portfolio_allocation_section (
        
        date : Optional[str] = None,
        fundation : Optional[str] = None,

    ) :
    """
    
    """

    dataframe = portfolio_allocation_analysis(date, fundation)
    dataframe = format_numeric_columns_to_string(dataframe)
    st.dataframe(dataframe)

    return None


# ----------- AUM Détails -----------

def aum_details_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        book_by_fund : Optional[Dict]= None

    ) :
    """
    Docstring for aum_details_section
    """
    date = date_to_str(date)
    
    left_h5(f"Total AUM Detail at {date}")

    dataframe, md5 = read_detailed_aum_from_cache(date)

    if dataframe is None :
        
        dataframe , md5 = fetch_subred_by_date(date)
        save_raw_aum_to_cache(dataframe, date)

    dataframe, md5 = clean_aum_by_fund(dataframe, md5, fundation)
    dataframe = format_numeric_columns_to_string(dataframe)
    
    show_aum_details_table(dataframe)

    return None,


# ----------- Script Agregated Positions -----------

def asset_class_aggregated_positions_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        last_gav : Optional[float] = None,

    ) :
    """
    Docstring for asset_class_aggregated_positions_section
    """
    left_h3(f"Asset Class Aggregated Positions")
    
    if st.button("Run Positions") :
        
        dataframe, md5, real_date = read_db_gross_data_by_date(date=date, fund=fundation)
        df_gav, _ = gav_performance_normalized_base_100(
            st.session_state.start_date_perf,
            st.session_state.end_date_perf,
            fundation,
        )

        last_gav = df_gav.select(pl.col("GAV").last()).item() if last_gav is None else last_gav
        aum = float(read_aum_from_cache(date).get(fundation, None).get("amount").replace(',', ''))

        last_gav = round(float(aum) * float(last_gav) / 100, 2)

        st.divider()
        cash_cascade_section(dataframe, md5, real_date, fundation, gav=last_gav)
        st.divider()
        fx_cascade_section(dataframe, md5, real_date, fundation, gav=last_gav)
        st.divider()
        exotic_cascade_section(dataframe, md5, real_date, fundation, gav=last_gav)
        st.divider()
        equity_cascade_section(dataframe, md5, real_date, fundation, gav=last_gav)
        st.divider()
        rates_cascade_section(dataframe, md5, real_date, fundation, gav=last_gav)

    return None


def cash_cascade_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        
        asset_class : str = "CASH",
        trade_types : List[str] = ["IM", "Cash Interest"],

        gav : Optional[float] = None,

    ) :
    """
    Docstring for cash_cascade_section
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5, real_date = asset_class_cascade_by_date(date=date, fund=fundation) if dataframe is None else (dataframe, md5, date)
    
    real_date = date_to_str(real_date)
    left_h5(f"Cash Cascade Table as of {real_date}")

    dataframe = dataframe.filter(pl.col("Asset Class") == asset_class)
    dataframe = dataframe.with_columns(

        pl.when(pl.col("Trade Type").is_in(trade_types))
        .then(pl.col("Trade Type"))
        .otherwise(pl.lit("Other"))
        .alias("Trade Type")
    
    )
    
    dataframe = dataframe.with_columns(
    
        pl.when((pl.lit(gav) != 0) & pl.col("MV").is_not_null())
        .then(pl.col("MV") / pl.lit(gav))
        .otherwise(None)
        .alias("MV/NAV %")
    
    )

    dataframe = dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(groupable=True, enableRowGroup=True, editable=False)

    gb.configure_column("Asset Class", rowGroup=True, hide=False)
    gb.configure_column("Counterparty", rowGroup=True, hide=False)
    gb.configure_column("Underlying Asset", rowGroup=True, hide=False)
    gb.configure_column("Trade Type", rowGroup=True, hide=False)
    gb.configure_column("MV", aggFunc="sum", valueFormatter="x.toFixed(2)", pinned="right")
    gb.configure_column("MV/NAV %", aggFunc="sum", valueFormatter="(x * 100).toFixed(4) + '%'", pinned="right")

    grid_options = gb.build()

    AgGrid(
        dataframe,
        gridOptions=grid_options    
    )
    
    return None


def fx_cascade_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        
        asset_class : str = "FX",
        gav : Optional[float] = None,

    ) :
    """
    Docstring for cash_cascade_section
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5, real_date = asset_class_cascade_by_date(date=date, fund=fundation, asset_class=asset_class) if dataframe is None else (dataframe, md5, date)

    if dataframe.is_empty() or dataframe is None :

        st.warning("No data avaialable for the selected date")
        return None
    
    real_date = date_to_str(real_date)
    left_h5(f"FX Cascade Table as of {real_date}")

    dataframe = dataframe.filter(pl.col("Asset Class") == asset_class)
    dataframe = dataframe.with_columns(
    
        pl.when((pl.lit(gav) != 0) & pl.col("MV").is_not_null())
        .then(pl.col("MV") / pl.lit(gav))
        .otherwise(None)
        .alias("MV/NAV %")
    
    )
    dataframe = dataframe.to_pandas()


    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(groupable=True, enableRowGroup=True, editable=False)

    gb.configure_column("Asset Class", rowGroup=True, hide=False)
    gb.configure_column("Counterparty", rowGroup=True, hide=False)
    gb.configure_column("Underlying Asset", rowGroup=True, hide=False)
    gb.configure_column("MV", aggFunc="sum", valueFormatter="x.toFixed(2)", pinned="right")
    gb.configure_column("MV/NAV %", aggFunc="sum", valueFormatter="(x * 100).toFixed(4) + '%'", pinned="right")

    grid_options = gb.build()

    AgGrid(
        dataframe,
        gridOptions=grid_options    
    )
    
    return None


def exotic_cascade_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        
        asset_class : str = "EXOTIC",
        gav : Optional[float] = None,

    ) :
    """
    Docstring for cash_cascade_section
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5, real_date = asset_class_cascade_by_date(date=date, fund=fundation, asset_class=asset_class) if dataframe is None else (dataframe, md5, date)

    if dataframe.is_empty() or dataframe is None :

        st.warning("No data avaialable for the selected date")
        return None
    
    real_date = date_to_str(real_date)
    left_h5(f"Exotic Cascade Table as of {real_date}")

    dataframe = dataframe.filter(pl.col("Asset Class") == asset_class)
    dataframe = dataframe.with_columns(
    
        pl.when((pl.lit(gav) != 0) & pl.col("MV").is_not_null())
        .then(pl.col("MV") / pl.lit(gav))
        .otherwise(None)
        .alias("MV/NAV %")
    
    )

    dataframe = dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(groupable=True, enableRowGroup=True, editable=False)

    gb.configure_column("Asset Class", rowGroup=True, hide=False)
    gb.configure_column("Counterparty", rowGroup=True, hide=False)
    gb.configure_column("Portfolio Name", rowGroup=True, hide=False)
    gb.configure_column("Product Name", rowGroup=True, hide=True)
    gb.configure_column("Product Code", rowGroup=True, hide=True)
    gb.configure_column("Instrument Type", rowGroup=True, hide=True)
    gb.configure_column("MV", aggFunc="sum", valueFormatter="x.toFixed(2)", pinned="right")
    gb.configure_column("MV/NAV %", aggFunc="sum", valueFormatter="(x * 100).toFixed(4) + '%'", pinned="right")

    grid_options = gb.build()

    AgGrid(
        dataframe,
        gridOptions=grid_options    
    )
    
    return None


def equity_cascade_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        
        asset_class : str = "EQUITY",
        gav : Optional[float] = None,

    ) :
    """
    Docstring for cash_cascade_section
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5, real_date = asset_class_cascade_by_date(date=date, fund=fundation, asset_class=asset_class) if dataframe is None else (dataframe, md5, date)

    if dataframe.is_empty() or dataframe is None :

        st.warning("No data avaialable for the selected date")
        return None
    
    real_date = date_to_str(real_date)
    left_h5(f"Equity Cascade Table as of {real_date}")

    dataframe = dataframe.filter(pl.col("Asset Class") == asset_class)
    dataframe = dataframe.with_columns(
    
        pl.when((pl.lit(gav) != 0) & pl.col("MV").is_not_null())
        .then(pl.col("MV") / pl.lit(gav))
        .otherwise(None)
        .alias("MV/NAV %")
    
    )

    dataframe = dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(groupable=True, enableRowGroup=True, editable=False)

    gb.configure_column("Asset Class", rowGroup=True, hide=False)
    gb.configure_column("Counterparty", rowGroup=True, hide=False)
    gb.configure_column("Portfolio Name", rowGroup=True, hide=False)
    gb.configure_column("Underlying Asset", rowGroup=True, hide=True)
    gb.configure_column("MV", aggFunc="sum", valueFormatter="x.toFixed(2)", pinned="right")
    gb.configure_column("MV/NAV %", aggFunc="sum", valueFormatter="(x * 100).toFixed(4) + '%'", pinned="right")

    grid_options = gb.build()

    AgGrid(
        dataframe,
        gridOptions=grid_options    
    )
    
    return None


def rates_cascade_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        
        asset_class : str = "EQUITY",
        gav : Optional[float] = None,

    ) :
    """
    Docstring for cash_cascade_section
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5, real_date = asset_class_cascade_by_date(date=date, fund=fundation, asset_class=asset_class) if dataframe is None else (dataframe, md5, date)

    if dataframe.is_empty() or dataframe is None :

        st.warning("No data avaialable for the selected date")
        return None
    
    real_date = date_to_str(real_date)
    left_h5(f"Rates Cascade Table as of {real_date}")

    dataframe = dataframe.filter(pl.col("Asset Class") == asset_class)
    dataframe = dataframe.with_columns(
    
        pl.when((pl.lit(gav) != 0) & pl.col("MV").is_not_null())
        .then(pl.col("MV") / pl.lit(gav))
        .otherwise(None)
        .alias("MV/NAV %")
    
    )

    dataframe = dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(groupable=True, enableRowGroup=True, editable=False)

    gb.configure_column("Asset Class", rowGroup=True, hide=False)
    gb.configure_column("Counterparty", rowGroup=True, hide=False)
    gb.configure_column("Portfolio Name", rowGroup=True, hide=False)
    gb.configure_column("Underlying Asset", rowGroup=True, hide=True)
    gb.configure_column("Issuer", rowGroup=True, hide=True)
    gb.configure_column("Product Code", rowGroup=True, hide=True)

    gb.configure_column("MV", aggFunc="sum", valueFormatter="x.toFixed(2)", pinned="right")
    gb.configure_column("MV/NAV %", aggFunc="sum", valueFormatter="(x * 100).toFixed(4) + '%'", pinned="right")

    grid_options = gb.build()

    AgGrid(
        dataframe,
        gridOptions=grid_options    
    )
    
    return None


