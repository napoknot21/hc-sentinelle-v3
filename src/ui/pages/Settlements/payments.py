from __future__ import annotations

import os
import streamlit as st

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_payments_selector, date_selector
from src.ui.components.input import (
    general_payment_fields, type_market_fields, amount_currency_fields,
    name_reference_bank_fields, bank_benificiary_fields, iban_field,
    extra_options_fields
)

from src.core.data.payments import (
    find_beneficiary_by_ctpy_ccy_n_type, process_excel_to_pdf, process_payments_to_excel, 
    create_payement_email
)

from src.config.parameters import (
    PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_TYPES_MARKET,
    PAYMENTS_REFERENCES_CTPY, PAYMENTS_ACCOUNTS
)


def payments_process (default_value : int = 1) :
    """
    Docstring for payments_process
    """
    nb_payments = nb_of_payments_section(default_value)
    cols = st.columns(nb_payments)

    payments = []

    for i, col in enumerate(cols) :

        with col :

            left_h5(f"Settlement {i+1}")
            
            date = value_date_section(number_order=i+1)
            amount, currency = amount_n_currency_section(number_order=i+1)

            payment = (date,amount,currency)
            payments.append(payment)

    return None



# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_payments_selector(min_value=default_value)

    return nb_payments



def value_date_section (number_order : int = 1) :
    """
    Docstring for value_date_section
    """
    date = date_selector("Value Date", key=f"settlements_date_{number_order}")

    return date



def amount_n_currency_section (currencies :  Optional[List[str]] = None, number_order : int = 1) :
    """
    Docstring for amount_n_currency_section
    
    :param number_order: Description
    :type number_order: int
    """
    key_amount = f"settlement_amaunt_{number_order}"
    key_currency = f"settlement_currency_{number_order}"

    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    amount, currency = amount_currency_fields(currencies, number_order, key_amount, key_currency)

    return amount, currency