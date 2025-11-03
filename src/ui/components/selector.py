from __future__ import annotations

import streamlit as st
import datetime as dt


from typing import Optional



def date_selector (
        
        label : str,
        default_value : Optional[str | dt.date | dt.datetime] = None,
        key : str = "date"
        
    ) :
    """
    
    """
    default_value = dt.datetime.now().date() if default_value is None else default_value

    return st.date_input(label, value=default_value, key=key)



def fundation_selector () :
    """
    
    """
    return None