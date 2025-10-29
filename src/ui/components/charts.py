from __future__ import annotations

import polars as pl
import pandas as pd

import streamlit as st
import plotly.express as px

from typing import Any, Optional

from src.utils.logger import log


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

