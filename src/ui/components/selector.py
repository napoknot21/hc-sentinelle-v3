from __future__ import annotations

import streamlit as st
import datetime as dt



def date_selector (label : str, type : dt.date = dt.datetime.now(), key : str = "date") :
    """
    
    """
    return st.date_input(label, value=type, key=key)




def fundation_selector () :
    """
    
    """
    return None