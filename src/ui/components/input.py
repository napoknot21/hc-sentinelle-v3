from __future__ import annotations

import polars as pl
import datetime as dt
from typing import Optional, List, Dict

import streamlit as st



def general_payment_fields (
        
        fundations : Optional[List[str]] = None,
        counterparties : Optional[List[str]] = None,
        account_numbers : Optional[List[str]] = None,

        number_order : int = 1,

    ) :
    """
    
    """

    fundation = st.selectbox("Fundation Name", options=fundations, key=f"Payment_process_{number_order}_fundation")
    counterparty = st.selectbox("Counterparty", options=counterparties, key=f"Payment_process_{number_order}_counterparty")
    account = st.selectbox("Account Number Payment", options=account_numbers, key=f"Payment_process_{number_order}_account")

    return fundation, counterparty, account


def type_market_fields (
        
        type_market : Optional[Dict] = None,
        types : Optional[List[str]] = None,
        number_order : int = 1,

    ) :
    """
    
    """

    type = st.selectbox("Type", options=types, key=f"Type_market_{number_order}_type")

    markets = type_market.get(type)
    market = st.selectbox("Market", options=markets, key=f"Type_market_{number_order}_market")

    return type, market