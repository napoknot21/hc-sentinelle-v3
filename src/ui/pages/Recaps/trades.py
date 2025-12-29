from __future__ import annotations

import streamlit as st
from src.core.api.recap import trade_recap_launcher

def trades () :
    """
    Docstring for trades
    """

    date = st.date_input("Choose a date")

    if st.button("Run Trade Recap") :

        trade_recap_launcher(date)

    return None




