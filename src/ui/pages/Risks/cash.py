from __future__ import annotations

import sys
import polars as pl
import streamlit as st
import pandas as pd
import datetime as dt

from typing import Optional, List, Dict

# Add of CCYs from LibApi
from src.config.paths import LIBAPI_ABS_PATH
sys.path.append(LIBAPI_ABS_PATH)

from src.config.parameters import SIMM_MAPPING_COUNTERPARTIES, SIMM_MAPPING_COUNTERPARTIES_BANK_CODE
from src.utils.dates import previous_business_day
from src.utils.formatters import str_to_date, format_numeric_columns_to_string

from src.ui.components.text import center_bold_paragraph, center_h2, left, left_h5
from src.ui.components.charts import cash_chart, history_criteria_graph, simm_vs_ice_graph

from src.core.data.cash import load_all_cash, load_all_collateral, aggregate_n_groupby, pivot_currency_historic, load_cache_fx_values
from src.core.data.simm import get_simm_all_history
from src.core.api.cash import call_api_for_pairs

# -------- Main function --------

def cash (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
        
    ) :
    """
    
    
    """
    date = previous_business_day(date)

    center_h2("Cash Per Counterparty")
    st.write('')
    
    cash_amount_section(date, fundation) 
    st.write('')

    collateral_detailed(date, fundation)
    st.write('')

    render_fx_metrics_section()
    
    im_n_collat_section(fundation)

    vm_n_requirement_section(fundation)

    net_excess_graph_session(fundation)
    st.write('')

    simm_vs_data_section(fundation)
    
    return None


# -------- Counterparty tables and charts --------

def cash_amount_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
    
    ) :
    """
    
    """
    dataframe, md5 = load_all_cash(fundation)
    col1, col2 = st.columns(2)

    with col1 :
        
        print(dataframe)
        cash_history_chart(dataframe, md5, ("Bank", "Type", "Date"), "Amount in EUR")
        
    with col2 :

        st.write('')
        st.write('')
        cash_per_ctpy_table(dataframe, md5, date, ("Bank", "Type"), "Amount in CCY")

        if st.button("Refresh Cash") :
            # TODO : Integrate Cash-Updater Script
            return None

    return None


def cash_history_chart (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        group_by : Optional[tuple[str, str]] = ("Bank", "Type", "Date"),
        aggregate : Optional[str] = "Amount in EUR"

    ) -> pl.DataFrame :
    """
    
    """
    df_grouped = (
        dataframe
        .group_by(list(group_by))
        .agg(pl.col(aggregate).sum().alias(aggregate))
        .sort("Date")
    )

    print(df_grouped)

    fig = cash_chart(df_grouped, md5, ("Bank", "Type"))
    
    st.plotly_chart(fig)
    
    return None


def cash_per_ctpy_table (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,

        group_by : Optional[tuple[str, str]] = ("Bank", "Type"),
        aggregate : Optional[str] = "Amount in CCY"

    ) :
    """
    
    """
    date = str_to_date(date)
    real_date = (dataframe.filter(pl.col("Date") <= date).select(pl.col("Date").max()).item())

    left_h5(f"Cash per counterparty, type and currency (Email data) until {real_date}")
    new_df, md5_hash = aggregate_n_groupby(dataframe, md5, date, group_by, aggregate)
    df_st = format_numeric_columns_to_string(new_df)
    st.dataframe(df_st)

    return None


# -------- Counterparty tables and charts --------

def collateral_detailed (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
    ) :
    """
    
    """
    dataframe, md5 = load_all_collateral(fundation=fundation)

    date = str_to_date(date)
    real_date = (dataframe.filter(pl.col("Date") <= date).select(pl.col("Date").max()).item())

    left_h5(f"Collateral per Counterparty Detailed until {real_date}")

    dataframe_dates = dataframe.filter(pl.col("Date") == real_date)

    if dataframe_dates.is_empty() :

        dates_series = (
            dataframe
            .select(pl.col("Date").unique().sort())
            .to_series()
        )

        # garder seulement les dates <= target_date
        prev_dates = dates_series.filter(dates_series <= date)

        if len(prev_dates) == 0:
            print("[!] No previous date available in dataframe.")
            return None, md5

        closest_date = prev_dates.max()
        print(f"[+] Using closest previous date: {closest_date}")

        dataframe_dates = dataframe.filter(pl.col("Date") == closest_date)

    df_st = format_numeric_columns_to_string(dataframe_dates)

    st.dataframe(df_st)

    return None


# -------- FX Values --------

def render_fx_metrics_section (values : Optional[Dict] = None, base : str = "EUR") :
    """
    Docstring for render_fx_metrics_section
    
    :param values: Description
    :type values: Optional[Dict]
    """
    values = fx_metrics_section() if values is None else values

    if values is None :
        return None
    
    left_h5("FX conversion values")

    ccys = [c for c in values.keys() if c != "EUR"]
    cols = st.columns(len(ccys))


    for ccy, col in zip(ccys, cols) :
        
        rate = values.get(ccy, 1.0)

        with col :

            label = f"{base} -> {ccy}"
            value_str = f"{rate:,.4f}"

            # Metrics
            st.metric(
                label=label,
                value=value_str,
            )

            st.markdown(
                f"<div style='font-size:0.75rem; color:#888;'>"
                f"1 {base} = {value_str} {ccy}"
                f"</div>",
                unsafe_allow_html=True,
            )

    return None


def fx_metrics_section () :
    """
    Docstring for fx_metrics_section
    """
    close_values = load_cache_fx_values()

    if close_values is not None :
        return close_values
    
    close_values = call_api_for_pairs(None)

    if close_values is not None :
        return close_values

    return None


# -------- IM & Collat columns -------- 

def im_n_collat_section (fundation : Optional[str] = None) :
    """
    Docstring for im_n_collat_section
    """
    col1, col2 = st.columns(2)

    with col1 :
        im_graph_section(fundation)

    with col2 :
        collat_graph_section(fundation)

    return None

 
def im_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for im_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "IM")
    
    st.plotly_chart(fig, width="content")

    return None


def collat_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for collat_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "Total")
    
    st.plotly_chart(fig, width="content")

    return None
    

# -------- VM & Req columns -------- 

def vm_n_requirement_section (fundation : Optional[str] = None) :

    """
    Docstring for vm_n_requirement_section
    """
    col1, col2 = st.columns(2)

    with col1 :
        vm_graph_section(fundation)

    with col2 :
        requirement_graph_section(fundation)

    return None


def vm_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for collat_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "VM")
    
    st.plotly_chart(fig, width="content")

    return None


def requirement_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for collat_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "Requirement")
    
    st.plotly_chart(fig, width="content")

    return None


def net_excess_graph_session (fundation : Optional[str] = None) :
    """
    Docstring for net_excess_graph_session
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "Net Excess/Deficit")
    
    st.plotly_chart(fig, width="content")

    return None


# -------- SIMM vs Data --------

def simm_vs_data_section (
        
        fundation : Optional[str] = None,
        banks : Optional[List[str]] = None,

        ctpy_rename : Optional[Dict] = None,
        bank_code : Optional[Dict] = None,
        columns : Optional[List[str]] = ["Bank", "Date", "IM", "VM"]
    
    ) :
    """
    Docstring for simm_vs_data_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    simm_df, simm_md5 = get_simm_all_history(fundation)

    ctpy_rename = SIMM_MAPPING_COUNTERPARTIES if ctpy_rename is None else ctpy_rename
    bank_code = SIMM_MAPPING_COUNTERPARTIES_BANK_CODE if bank_code is None else bank_code

    dataframe = (
        dataframe.filter(pl.col("Currency") == "EUR")
        .select(columns)
        .rename({"IM": "IM_data", "VM": "VM_data"})
        .with_columns(
            (-pl.col("IM_data")).alias("IM_data")
        )
        .sort("Date")
    )

    simm_df, simm_md5 = simm_vs_data_data_normalization(simm_df, simm_md5, ctpy_rename, bank_code)
    simm_df = (
        simm_df
        .select(columns)
        .rename({"IM": "IM_ice", "VM": "VM_ice"})
        .sort("Date")
    )
    
    joined = dataframe.join(simm_df, on=columns[0:2], how="outer", coalesce=True).sort("Date")

    banks = list(bank_code.values()) if banks is None else banks

    # Persist le choix dans session_state
    if "simm_bank_selector" not in st.session_state:
        st.session_state["simm_bank_selector"] = banks[0]

    bank_selector = st.selectbox("Select Bank for SIMM vs Data", options=banks, key="simm_bank_selector")

    im_n_vm_simm_vs_data_section(joined, md5, bank_selector)  

    return None


def simm_vs_data_data_normalization (
        
        simm_df : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        ctpy_rename : Optional[Dict] = None,
        bank_code : Optional[Dict] = None
    
    ) -> tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    Docstring for simm_vs_data_data_normalization
    """
    if simm_df is None :
        return None, None
    
    # Normalization of Counterparties names between Data and SIMM
    ctpy_rename = SIMM_MAPPING_COUNTERPARTIES if ctpy_rename is None else ctpy_rename
    bank_code = SIMM_MAPPING_COUNTERPARTIES_BANK_CODE if bank_code is None else bank_code

    simm_df = (
        
        simm_df
        .with_columns(pl.col("Counterparty").replace(ctpy_rename))
        .with_columns(pl.col("Counterparty").replace(bank_code))
        .rename({"Counterparty": "Bank", "MV": "VM"})
        # Cast Date en pl.Date pour matcher dataframe (qui est pl.Date, pas Datetime)
        .with_columns(pl.col("Date").cast(pl.Date))
    
    )

    return simm_df, md5


def im_n_vm_simm_vs_data_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        bank : Optional[str] = None
    
    ) -> None :
    """
    Docstring for im_n_vm_simm_vs_data_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    col1, col2 = st.columns(2)

    with col1 :
        im_simm_vs_data_section(dataframe, md5, bank)

    with col2 :
        vm_simm_vs_data_section(dataframe, md5, bank)

    return None


def im_simm_vs_data_section (dataframe : Optional[pl.DataFrame] = None, md5 : Optional[str] = None, bank : Optional[str] = None) :
    """
    Docstring for im_simm_vs_data_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe = dataframe.filter(pl.col("Bank") == bank)
    fig = simm_vs_ice_graph(dataframe, md5, "IM")
    
    st.plotly_chart(fig, width="content")

    return None


def vm_simm_vs_data_section (dataframe : Optional[pl.DataFrame] = None, md5 : Optional[str] = None, bank : Optional[str] = None) :
    """
    Docstring for vm_simm_vs_data_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe = dataframe.filter(pl.col("Bank") == bank)
    fig = simm_vs_ice_graph(dataframe, md5, "VM")
    
    st.plotly_chart(fig, width="content")

    return None



