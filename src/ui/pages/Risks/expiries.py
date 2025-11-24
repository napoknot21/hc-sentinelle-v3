from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import Dict, List, Optional

from src.config.parameters import EXPIRIES_COLUMNS_SPECIFIC

from src.core.data.expiries import load_upcomming_expiries

from src.ui.components.charts import expiries_plot
from src.ui.components.tables import show_last_n_expiries, show_expiries_history
from src.ui.components.text import center_h2, left_h5


def expiries (date : Optional[str | dt.date | dt.datetime] = None, fundation : Optional[str] = None) :
    """
    
    """
    center_h2("Upcoming Expiries")
    st.write('')

    upcoming_expiries_section(date, fundation)
    st.write('')
    st.write('')
    all_expiries_section(date, fundation)

    return None


# ---------- Upcoming Experies ---------- 

def upcoming_expiries_section (date : Optional[str | dt.date | dt.datetime] = None, fundation : Optional[str] = None,) :
    """
    
    """
    col1, col2 = st.columns(2)
    
    with col1 :
        chart_experies_per_week_section(date, fundation)
        
    with col2 :
        table_n_last_expiries(date, fundation)

    return None


def chart_experies_per_week_section (date : Optional[str | dt.date | dt.datetime] = None, fundation : Optional[str] = None, title : str = "Number of Expiries per Day") :
    """
    
    """
    dataframe, md5 = load_upcomming_expiries(date, fundation)

    fig = expiries_plot(dataframe, title, "Termination Date", md5)
    st.plotly_chart(fig)
    
    return None


def table_n_last_expiries (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,
        n_expiries : int = 10,
        specific_cols : Dict = None,
           
    ) :
    """
    
    """
    specific_cols = list(EXPIRIES_COLUMNS_SPECIFIC.keys()) if specific_cols is None else specific_cols
    dataframe, md5 = load_upcomming_expiries(date, fundation)

    title = f"Next {n_expiries} expiries"

    left_h5(title)
    show_last_n_expiries(dataframe, md5, specific_cols, max_rows=n_expiries)
    
    return None


# ---------- Exprires history ----------

def all_expiries_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

    ) :
    """

    """
    dataframe, md5 = load_upcomming_expiries(date, fundation)
    show_expiries_history(dataframe, md5)
    
    return None
