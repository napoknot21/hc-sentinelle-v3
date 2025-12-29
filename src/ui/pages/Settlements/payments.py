from __future__ import annotations

import os
import streamlit as st

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_items_selector, date_selector
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

from src.utils.data_io import convert_ubs_instruction_payments_to_excel, export_excel_to_pdf


def payments_process (default_value : int = 1) :
    """
    Docstring for payments_process
    """
    center_h2("Process Payments")
    nb_payments = nb_of_payments_section(default_value)

    payments = input_payment_section(nb_payments)

    st.write('')
    left_h5("Export Option")

    #email, book = extra_options_section()
    
    if st.button("Process Payments") :
        process_payements_section(payments)#, email, book)

    return None
   


# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_items_selector(min_value=default_value)

    return nb_payments


def input_payment_section (nb_payments : int = 1) :
    """
    Docstring for payment_section
    
    :param nb_payments: Description
    :type nb_payments: int
    """
    cols = st.columns(nb_payments)
    payments = []

    for i, col in enumerate(cols) :

        with col :

            left_h5(f"Settlement {i+1}")
            
            date = value_date_section(number_order=i+1)
            amount, currency = amount_n_currency_section(number_order=i+1)

            payment = (None, None, None, None, None, None, amount, currency, date, None, None, None, None)
            payments.append(payment)

    return payments




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
    key_amount = f"UBS_Settlement_amount_{number_order}"
    key_currency = f"UBS_Settlement_currency_{number_order}"

    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    amount, currency = amount_currency_fields(currencies, number_order, key_amount, key_currency)

    return amount, currency


def process_payements_section (
        
        payments : Optional[List] = None,

    ) :
    """
    Docstring for process_payements_section
    
    :param payments: Description
    :type payments: Optional[List]
    """
    response = convert_ubs_instruction_payments_to_excel(payments)

    status = response["success"]

    if status is True :

        pdf_status = export_excel_to_pdf(response.get("path"), "Paymentsdsds.pdf")
        
        st.warning(f"{response["message"]}")
        st.warning(f"Successfully at {response.get("path")}")



    else :
        
        st.error(f"{response["message"]}")

    return None