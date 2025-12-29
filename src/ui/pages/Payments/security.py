from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.config.parameters import PAYMENTS_CONCURRENCIES, PAYMENTS_FUNDS, PAYMENTS_ACCOUNTS

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_items_selector
from src.ui.components.input import amount_currency_fields, general_payment_fields


def security (min_default_value : int = 1) :
    """
    Docstring for security
    """
    center_h2("Process Securities")
    nb_securities = nb_of_securities_section(min_default_value)
    
    securities = securities_section(nb_securities)

    return None


# ----------- Nb of Securities selector -----------

def nb_of_securities_section (
        
        default_value : int = 1,
        label : str = "Select number of Securities"
    
    ) :
    """
    
    """
    nb_securities = number_of_items_selector(label=label, min_value=default_value)

    return nb_securities


# ----------- Input Section -----------

def securities_section (nb_securities : int = 1) :
    """
    
    """
    cols = st.columns(nb_securities)
    securities = []

    for i, column in enumerate(cols) :

        with column :

            security = input_security_section(i)
            securities.append(security)

    return securities


def fund_n_portfolio_id_section (
        
        fundations : Optional[List[str]] = None,
        portfolio_ids : Optional[List[str]] = None,

        key_fund : Optional[str] = None,
        key_portf_id : Optional[str] = None,

        number_order : int = 1,

    ) :
    """
    Docstring for fund_section
    
    :param fundation: Description
    :type fundation: Optional[List[str]]
    """
    fundations = PAYMENTS_FUNDS if fundations is None else fundations
    portfolio_ids = PAYMENTS_ACCOUNTS if portfolio_ids is None else portfolio_ids

    key_fundation = f"Payment_security_{number_order}_fundation"
    key_portf_id = f"Payment_security_{number_order}_portfolio_id"

    fundation, portfolio_id = general_payment_fields(fundations, None, portfolio_ids, number_order)
    
    return None #fundation, counterparty, account


def input_security_section (i : int = 1) :
    """
    Docstring for input_security_section
    
    :param default_value: Description
    :type default_value: int
    """
    center_h5(f"Security {i+1}")

    amount, ccy = amount_currency_fields()
