from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import Dict, List, Optional

from src.config.parameters import EXPIRIES_COLUMNS_SPECIFIC

from src.core.data.expiries import load_upcomming_expiries, get_upcomming_expiries_file_by_date

from src.ui.components.charts import expiries_plot
from src.ui.components.tables import show_last_n_expiries
from src.ui.components.text import center_h2, left_h3, left_h5


def expiries (date : Optional[str | dt.date | dt.datetime] = None, fundation : Optional[str] = None) :
    """
    
    """
    center_h2("Upcoming Expiries")
    st.write('')

    col1, col2 = st.columns(2)
    
    with col1 :

        fig = chart_experies_per_week(date, fundation)
        
        if fig is not None :
            st.plotly_chart(fig)

        else :
            st.warning("No file was founded. Relaunch")
        
    with col2 :
        table_n_last_expiries(date, fundation)



def chart_experies_per_week (date : Optional[str | dt.date | dt.datetime] = None, fundation : Optional[str] = None, title : str = "Number of Expiries per Day") :
    """
    
    """
    dataframe, md5 = load_upcomming_expiries(date, fundation)
    fig = expiries_plot(dataframe, title, "Termination Date", md5)

    return fig


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
    table = show_last_n_expiries(dataframe, md5, specific_cols, max_rows=n_expiries)

    return table

