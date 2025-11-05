from __future__ import annotations

import polars as pl
import pandas as pd
import datetime as dt

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from typing import Any, Optional, List, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str


@st.cache_data()
def expiries_plot (
    
        _dataframe : pl.DataFrame,
        title : str,
        group_by : str,
        md5 : str,

        width : int = 500,
        height : int = 500,
    
    ) -> Any :
    """
    
    """
    if _dataframe is None or _dataframe.is_empty() :
        
        st.cache_data.clear()
        return None
    
    # Validate
    if group_by not in _dataframe.columns :
        
        log(f"Column '{group_by}' not in DataFrame: {_dataframe.columns}", "error")
        return None
    
    counts = (

        _dataframe
        .group_by(group_by)
        .len()
        .rename(
            {
                group_by : "Group",
                "len" : "Number of Expiries"
            }
        )
        .sort("Group")
    )

    # Plotly from plain lists (no pandas dependency)
    x = counts["Group"].to_list()
    y = counts["Number of Expiries"].to_list()

    fig = px.bar(

        x=x,
        y=y,
        title=title,
        labels={"x" : group_by, "y" : "Number of Expiries"},
        #color=y,  # enables the continuous color scale
        color_continuous_scale=px.colors.sequential.Blues,

    )

    fig.update_xaxes(type="category")
    fig.update_layout(

        width=width,
        height=height,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_color="black", font_size=16),
        margin=dict(l=0, r=20, t=30, b=0),
    
    )

    return fig


@st.cache_data()
def nav_estimate_performance_graph (
        
        _dataframe : pl.DataFrame,
        md5 : str,

        fundation : str,
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,
        
        y_colonnes : Optional[List[str]] = None,
        x_colonne : Optional[str] = None,

        yaxis_title : str = "GAV (%)"

    ) : 
    """
    
    """
    if _dataframe is None :
        
        log("No dataframe entered. Returning a None chart...", "error")
        st.cache_data.clear()

        return None

    end_date = date_to_str() if end_date is None else end_date
    start_date = date_to_str() if start_date is None else start_date
    
    fig = go.Figure()

    x_colonne_data = _dataframe[x_colonne]

    for y_colonne in y_colonnes :
        
        y_colonne_data = _dataframe[y_colonne]

        fig.add_trace(

            go.Scatter(
                x=x_colonne_data,
                y=y_colonne_data,
                mode="lines",
                name=y_colonne,
                line_shape="spline"
            )

        )

    fig.update_layout(

        xaxis_title=x_colonne,
        yaxis_title=yaxis_title,

        xaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=14),  # Adjust tick font size and color
            showticklabels=True,  # Ensure tick labels are shown
        ),

        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=14),  # Adjust tick font size and color
            showticklabels=True,  # Ensure tick labels are shown
        ),

        hovermode="x unified",

        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        ),

        height=350, 
        width=1600,

        margin=dict(l=0, r=0, t=0, b=0),  # Set margins to 0 to remove any padding
    
    )
    print(_dataframe)

    return fig


@st.cache_data()
def cash_chart (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        group_by : Optional[Tuple] = ("Bank", "Type"),
        currency : Optional[str] = "EUR"
    ) :
    """
    
    """
    if _dataframe is None :
        
        log("[-] Error loading the dataframe to plot", "error")
        st.cache_data.clear()

        return None
    
    agents = _dataframe.select(list(group_by)).unique()

    # Plot using Plotly
    fig = go.Figure()

    # Iterate through columns and add each one as a trace to the figure
    for row in agents.iter_rows() :

        bank, type_ = row[0], row[1]

        filtered_df = _dataframe.filter(
            (pl.col('Bank') == bank) & (pl.col('Type') == type_)
        )

        # Extract Date and EUR values for this combination
        filtered_df = filtered_df.sort("Date")

        dates = filtered_df['Date'].to_list()
        ccy_values = filtered_df[currency].to_list()

        fig.add_trace(

            go.Scatter(

                x=dates,
                y=ccy_values,
                mode='lines',
                stackgroup='one',
                name=f"{bank} - {type_}"
            )
            
        )

    # Layout settings for the plot
    fig.update_layout(

        title="Stacked Area: Summed Amount in EUR Over Time by Bank and Type",

        xaxis_title="Date",
        yaxis_title=f"Amount in {currency}",

        legend_title="Bank - Type",
        template="plotly_white",
        
        xaxis=dict(showgrid=True),  # Display grid on x-axis
        yaxis=dict(showgrid=True)   # Display grid on y-axis
    )

    return fig


@st.cache_data()
def simm_ctpy_im_vm_chart (
        

        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,

        x_axis : Optional[str] = None,
        columns : Optional[Tuple] = None,

    ) :
    """
    
    """
    if _dataframe is None :
        
        log("[-] Error loading the dataframe to SIMM chart", "error")
        st.cache_data.clear()

        return None
    
    counterparties = list(_dataframe[x_axis].unique())
    columns = list(columns)
    print(columns)
    
    # Plot using Plotly
    fig = go.Figure()

    for column in columns :
        fig.add_trace(go.Bar(x=counterparties, y=_dataframe[column], name=column))

    fig.update_layout(

        title=f"Most Recent SIMM Data at {date} (ICE Data)",
        xaxis=dict(title=x_axis),
        yaxis=dict(title='Amount'),
        hovermode="x unified",
        
        hoverlabel=dict(

            bgcolor="white",
            font_color="black",
            #font_size=16,
        ),

    )
    
    return fig

