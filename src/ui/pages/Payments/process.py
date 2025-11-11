from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import List, Optional, Dict

from src.ui.components.text import center_h2, center_h3, center_h5
from src.ui.components.selector import number_of_payments_selector
from src.ui.components.input import general_payment_fields, type_market_fields

from src.config.parameters import PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_TYPES


def process (default_value : int = 1) :
    """
    Main function that displays the Payments Process page
    """
    center_h2("Process Payments")
    nb_payments = nb_of_payments_section(default_value)

    payments_section(nb_payments)

    return None



def nb_of_payments_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_payments_selector(min_value=default_value)

    return nb_payments


def payments_section (nb_payments : int = 1) :
    """
    
    """
    cols = st.columns(nb_payments)

    for i, column  in enumerate(cols) :

        with column :

            center_h5(f"Payment {i+1}")
            fund, ccty, acc = input_payment_section(number_order=i+1)
            type, market = type_payment_section(number_order=i+1)




    return None


def input_payment_section (

        fundations : Optional[List[str]] = None,
        counterparties : Optional[List[str]] = None,
        accounts : Optional[List[str]] = None,

        number_order : int = 1,

    ) :
    """
    
    """
    fundations = PAYMENTS_FUNDS if fundations is None else fundations
    counterparties = PAYMENTS_CONCURRENCIES if counterparties is None else counterparties # TODO: Temp variable, next time change

    fundation, counterparty, account = general_payment_fields(fundations, counterparties, accounts, number_order)
    
    return fundation, counterparty, account


def type_payment_section (
        
        type_market : Optional[Dict] = None,
        number_order : int = 1,

    ) :
    """
    
    """
    type_maket = PAYMENTS_TYPES if type_market is None else type_market
    types = list(type_maket.keys())
    
    type, market = type_market_fields(type_market, types, number_order)

    return type, market
