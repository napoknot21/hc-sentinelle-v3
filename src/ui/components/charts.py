from __future__ import annotations

import polars as pl
import pandas as pd
import datetime as dt

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from typing import Any, Optional, List

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
