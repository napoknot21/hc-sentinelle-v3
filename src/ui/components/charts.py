from __future__ import annotations

import polars as pl
import pandas as pd
import datetime as dt

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from typing import Any, Optional, List, Tuple, Dict

from src.utils.logger import log
from src.utils.formatters import date_to_str, str_to_date, filter_token_col_from_df


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


@st.cache_data()
def simm_over_time_chart (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        title : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,

        x_axis : Optional[str] = None,
        column : Optional[str] = None,

    ) :
    """
    
    """
    if _dataframe is None :
        
        log(f"[-] Error loading the dataframe to {column} chart", "error")
        st.cache_data.clear()

        return None
    
    _dataframe = _dataframe.sort("Date")

    counterparties = list(_dataframe[x_axis].unique())

    # Plot using Plotly
    fig = go.Figure()

    traces = []
    for counterparty in counterparties :
        
        subset = _dataframe.filter(pl.col(x_axis) == counterparty)
        
        trace = go.Scatter(x=subset['Date'], y=subset.get_column(column), mode='lines', name=counterparty, line_shape='spline')
        traces.append(trace)
       
        #fig.add_trace(go.Bar(x=counterparties, y=_dataframe[column], name=column))

    layout = go.Layout(

        title=title,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Amount'),
        hovermode="x unified",

        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        ),
        
    )

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    return fig


@st.cache_data()
def total_nav_over_time_chart (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        title : Optional[str]  = None,

    ) :
    """
    
    """
    if _dataframe is None :

        st.cache_data.clear()
        return None
    
    date = str_to_date(date) if date is None else date
    dataframe = _dataframe.filter(pl.col("Date") <= date)
    
    trace_nav = go.Scatter(

        x=dataframe.get_column("Date"),
        y=dataframe.get_column("NAV"),
        
        mode='lines',
        name=title,
        line_shape='spline',
        line=dict(color='blue', width=2)  # Set line color to red

    )

    layout_nav = go.Layout(

        title=title,
    
        xaxis=dict(title='Date'),
        yaxis=dict(title='NAV'),

        hovermode="x unified",

        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        ),

        legend=dict(
            title="Sources",
            x=0.01,
            y=0.99,
        ),
    
    )
    
    fig = go.Figure(data=[trace_nav], layout=layout_nav)

    return fig


@st.cache_data()
def im_mv_over_nav_with_rolling (

        _dataframe : Optional[pl.DataFrame] = None,
        md5_1 : Optional[str] = None,
        md5_2 : Optional[str] = None,

        column : Optional[str] = None,

    ) :
    """
    
    """
    if _dataframe is None :
        
        st.cache_data.clear()
        return None

    columns = [

        {
            "name" : f"{column}/NAV %",
            "title" : f"Total {column} Over NAV %",
            "color" : "red"
        },

        {
            "name" : f"Rolling {column}/NAV %",
            "title" : f"Total Rolling {column} Over NAV %",
            "color" : "blue"
        },
        
    ]

    df_rolling = _dataframe.clone()
    df_rolling = df_rolling.sort("Date").with_columns(

        pl.col(f"{column}/NAV %")
            .rolling_mean(window_size=30, center=True)
            .alias(f"Rolling {column}/NAV %")

    )

    traces = []

    for column_nav in columns :

        trace = go.Scatter(

            x=df_rolling.get_column("Date"),
            y=df_rolling.get_column(column_nav["name"]),

            mode='lines',
            name=column_nav["title"],

            line_shape='spline',
            line=dict(color=column_nav["color"], width=2) # Set line color to red
            
        )

        traces.append(trace)

    # Create layout for the figure
    layout1 = go.Layout(

        title=f"Total {column} Over NAV %",
        xaxis=dict(title='Date'),
        yaxis=dict(title=f'{column}/NAV %'),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        ),
        legend=dict(
            title="Sources",
            x=0.01,
            y=0.99,
        ),
    )

    fig = go.Figure(data=traces, layout=layout1)

    return fig


@st.cache_data()
def leverage_line_chart (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        title : str = "Leverage over time",
        date : Optional[str | dt.datetime | dt.date] = None,
        
        columns : Optional[List[str]] = None,
        x_axis : Optional[str] = "Date"

    ) :
    """
    
    """
    if _dataframe is None :

        st.cache_data.clear()
        log("[-] No Dataframe available", "error")

        return None
    
    if not columns :
        
        st.cache_data.clear()
        log("[-] No columns provided to plot", "error")
        
        return None

    date = str_to_date(date)

    df = _dataframe.sort(x_axis)
    df = df.filter(
        pl.any_horizontal([pl.col(c).is_not_null() for c in columns])
    )
    df = df.filter(pl.col(x_axis) <= pl.lit(date))

    x_values = df.get_column(x_axis).to_list()

    # Plot using Plotly
    fig = go.Figure()

    for column in columns :

        if column not in df.columns :

            log(f"[-] Column '{column}' not in dataframe", "warning")
            continue
        
        y_values = df.get_column(column).to_list()

        fig.add_trace(

            go.Scatter(
            
                x=x_values,
                y=y_values,
                mode="lines",
                name=column,
                line_shape="spline",
            
            )

        )

        
    fig.update_layout(

        title=title,
        xaxis=dict(title=x_axis),
        yaxis=dict(title="Leverages"),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        ),
    )
        
    return fig
    

@st.cache_data()
def leverage_per_underlying_histogram (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        title : Optional[str] = None,

        x_axis : Optional[str] = None,
        y_axis : Optional[str] = None

    ) :
    """
    
    """

    if _dataframe is None :

        log("Error during Leverage per Underlying histogram, DF is empty.")
        st.cache_data.clear()

        return None
    
    _dataframe = _dataframe.with_columns(
        ((pl.col(y_axis) + 500)  // 1000 * 1000).alias(y_axis)
    )

    hist = px.histogram(

        _dataframe,
        title=title,
        x=x_axis,
        y=y_axis,
        text_auto=True
    
    )

    hist.update_layout(

        height=800,
        width=1700,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        )

    )

    hist.update_yaxes(showgrid=False)

    return hist


@st.cache_data()
def leverage_per_trade_histogram (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        
        title : Optional[str] = None,

        x_axis : Optional[str] = None,
        y_axis : Optional[str] = None,

        color : Optional[str] = None,

    ) :
    """
    
    """

    if _dataframe is None :

        log("Error during Leverage per Underlying histogram, DF is empty.")
        st.cache_data.clear()

        return None

    df_grouped = _dataframe.group_by(x_axis).agg(
        pl.col(y_axis).sum().alias(y_axis)
    )
    
    df_grouped = df_grouped.sort(x_axis)

    print(df_grouped)

    fig = go.Figure()

    fig.add_trace(
        
        go.Bar(

            name=y_axis,
            x=df_grouped.get_column(x_axis),
            y=df_grouped.get_column(y_axis),
            marker_color=color
        
        )
    
    )

    fig.update_layout(

        title=title,
        xaxis_title=x_axis,
        yaxis_title=y_axis

    )

    return fig


@st.cache_data()
def show_history_greeks_graph (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        asset_class : Optional[str] = None,
        greek : Optional[str] = None,

        greek_rules : Optional[Dict] = None,
        format : str = "%Y/%m/%d"
    
    ) :
    """
    
    """
    if _dataframe is None :

        st.cache_data.clear()
        return None
    

    token = greek_rules.get(asset_class)
    df_filtered = filter_token_col_from_df(_dataframe, "Underlying", token)

    if df_filtered.is_empty() :
        return None

    if df_filtered["Date"].dtype == pl.Utf8 :
        # adapte le format si 
        df_filtered = df_filtered.with_columns(
            pl.col("Date").str.strptime(pl.Date, format="%Y/%m/%d", strict=False)
        )
    
    df_filtered = df_filtered.sort("Date")

    underlyings = df_filtered.get_column("Underlying").unique().to_list()
    
    fig = go.Figure()

    for ul in underlyings :

        df_ul = df_filtered.filter(pl.col("Underlying") == ul).sort("Date")

        # Convert Polars Series -> Python lists for Plotly
        x_vals = df_ul.get_column("Date").to_list()
        y_vals = df_ul.get_column(greek).to_list()


        # Ligne plus épaisse pour les Totaux
        width = 2 if "Total" in str(ul) else 1

        fig.add_trace(

            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name=str(ul),
                line_shape="spline",
                line=dict(width=width),
            )

        )

    n_traces = len(fig.data)

    fig.update_layout(

        title=f"{greek} history by Underlying ({asset_class})",
        xaxis=dict(title="Date"),
        yaxis=dict(title=greek),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
        ),

        legend=dict(
            font=dict(size=10),
            yanchor="top",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            itemsizing="trace",
            orientation="v",
        ),

        updatemenus=[

            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.15,
                showactive=False,
                buttons=[
                    dict(
                        label="Select All",
                        method="update",
                        args=[{"visible": [True] * n_traces}],
                    ),
                    dict(
                        label="Unselect All",
                        method="update",
                        args=[{"visible": ["legendonly"] * n_traces}],
                    ),
                ],
            )
        ],

        height=800,
    )

    return fig