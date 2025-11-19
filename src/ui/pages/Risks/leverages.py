from __future__ import annotations

import polars as pl
import streamlit as st
import datetime as dt

from typing import Optional

from src.core.data.leverages import read_history_leverages, read_underlying_leverages, read_trade_leverages

from src.ui.components.charts import leverage_line_chart, leverage_per_underlying_histogram, leverage_per_trade_histogram
from src.ui.components.text import center_h2, left_h5


def leverages (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    center_h2("Leverages")

    leverage_analysis_graph_section(date, fundation)
    leverage_per_underlying_section(date, fundation)
    st.write('')
    leverage_per_trade_section(date, fundation)

    return None


# ----------- History Leverage -----------

def leverage_analysis_graph_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) -> None :
    """
    
    """
    dataframe, md5 = read_history_leverages(date, fundation)
    print(dataframe)

    title = f"Leverage over time until {date}"
    fig = leverage_line_chart(dataframe, md5, title, date, ["Gross Leverage", "Commitment Leverage"], "Date")
    
    st.plotly_chart(fig)

    return None


# ----------- Leverage per Underlying -----------

def leverage_per_underlying_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) -> None :
    """
    
    """
    dataframe, md5 = read_underlying_leverages(date, fundation)

    dt_date = dataframe.get_column("Date").item(0)
    title = f"Leverage per Underlying Distribution until {dt_date}"

    hist = leverage_per_underlying_histogram(
        dataframe,
        md5,
        title,
        "Underlying Asset",
        "Gross Leverage"
    )

    st.plotly_chart(hist, use_container_width = True)

    return None


# ----------- Leverage per Trade -----------

def leverage_per_trade_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) -> None :
    """
    
    """
    leverage_trade_asset_class_section(date, fundation)
    leverage_trade_full_hist_section(date, fundation)

    return None



def leverage_trade_asset_class_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    dataframe, md5 = read_trade_leverages(date, fundation)
    print(dataframe)
    dt_date = dataframe.get_column("Date").item(0)

    x_axis = "Asset Class"
    y_axis_1 = "Gross Leverage"
    y_axis_3 = "Exposure % NAV"

    col1, col2, col3 = st.columns(3)

    with col1 :
        
        title_1 = f"{y_axis_1} par Asset Class until {dt_date}"

        hist_1 = leverage_per_trade_histogram(
            dataframe,
            md5,
            title_1,
            x_axis,
            y_axis_1,
            "steelblue"
        )

        st.plotly_chart(hist_1, use_container_width = True)

    with col2 :

        for i in range(2) :
            st.write('')

        left_h5(f"Leverages per Asset Class Recap at {dt_date}")

        for i in range(4) :
            st.write('')

        df_grouped_1 = dataframe.group_by("Asset Class").agg(
            pl.col(y_axis_1).sum().alias(y_axis_1)
        )

        df_grouped_3 = dataframe.group_by("Asset Class").agg(
            pl.col(y_axis_3).sum().alias(y_axis_3)
        )

        df_grouped = df_grouped_1.join(df_grouped_3, on=x_axis) #([df_grouped_1, df_grouped_3], how="vertical")

        st.dataframe(df_grouped)

    with col3 :

        
        title_3 = f"{y_axis_3} par Asset Class until {dt_date}"

        hist_3 = leverage_per_trade_histogram(
            dataframe,
            md5,
            title_3,
            x_axis,
            y_axis_3,
            "indianred"
        )

        st.plotly_chart(hist_3, use_container_width = True)

    return None



def leverage_trade_full_hist_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    dataframe, md5 = read_trade_leverages(date, fundation)
    print(dataframe)

    dt_date = dataframe.get_column("Date").item(0)
    st.write('')
    left_h5(f"Leverages per Trades until {dt_date}")

    st.dataframe(dataframe)
    
    return None