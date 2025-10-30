from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import Dict, List, Optional

from src.ui.components.text import center_h2, center_h3



def portfolio (
    
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,

        title : str = "Historical NAV"    
    ) :
    """
    
    """
    # Title of the option menu
    center_h2(title)
    st.write('')

    col1, col2, col3 = st.columns(3)

    with col1 :

        weighted_performance(end_date=date, fundation=fundation,)

    


def weighted_performance (
        
        title : str = "Weighted Performance",
        start_date : Optional[str | dt.date | dt.datetime] = "2023-07-04",
        end_date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,
                
    ) :
    """
    
    """
    return None
    

