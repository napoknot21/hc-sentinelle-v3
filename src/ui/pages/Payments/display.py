from __future__ import annotations

import streamlit as st

from src.ui.components.text import center_h2, left_h5
from src.ui.components.tables import display_payments_table

from src.core.data.payments import load_payments_db, load_securities_db

def display () :
    """

    """
    center_h2("Display Payments")

    margin_calls_section()
    st.write('')
    securities_section()

    return None



def margin_calls_section () :
    """
    
    """
    left_h5("Margin Calls and Option Premiums")
    
    df, md5 = load_payments_db()

    if df is None :
        st.warning("Error during reading the file")

    else :
        display_payments_table(df, md5)



def securities_section () :
    """
    
    """
    left_h5("Securities")

    df, md5 = load_securities_db()

    if df is None :
        st.warning("Error during reading the file")

    else :
        display_payments_table(df, md5)
