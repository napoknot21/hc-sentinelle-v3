from __future__ import annotations

import os
import streamlit as st

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_items_selector, date_selector
from src.ui.components.input import (
    general_payment_fields, amount_currency_fields, type_return_fields, ubs_broker_fields
)

from src.core.data.payments import (
    find_beneficiary_by_ctpy_ccy_n_type, process_excel_to_pdf, process_payments_to_excel, 
    create_payement_email, load_beneficiaries_db
)

from src.config.parameters import (
    PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_BOOKS,
    PAYMENTS_DIRECTIONS, PAYMENTS_ACCOUNTS, PAYMENTS_BENEFICIARY_COLUMNS, PAYMENTS_BENECIFIARY_SHEET_NAME
)
from src.config.paths import UBS_PAYMENTS_DB_SSI_ABS_PATH
from src.utils.formatters import date_to_str


def security (default_value : int = 1) :
    """
    Docstring for payments_process
    """
    center_h2("UBS Securities")
    nb_payments = nb_of_securities_section(default_value)

    securities = input_payment_section(nb_payments)

    st.write('')
    left_h5("Export Option")

    #email, book = extra_options_section()
    
    if st.button("Process Payments") :
        process_securities_section(securities)#, email, book)

    return None
   


# ----------- Nb of Payement's selector -----------

def nb_of_securities_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_items_selector(
        label="Select number of Securities", min_value=default_value
    )

    return nb_payments


def input_payment_section (nb_payments : int = 1) :
    """
    Docstring for payment_section
    
    :param nb_payments: Description
    :type nb_payments: int
    """
    cols = st.columns(nb_payments)
    securities = []

    for i, col in enumerate(cols) :

        with col :

            center_h5(f"Security {i+1}")
            _, ctpy, acc = fund_ctpy_n_acc_section(number_order=i+1)
            """
            product, trade_ref = product_n_trade_ref_section(number_order=i+1)
            
            _, market = type_market_section(number_order=i+1)
            
            date = value_date_section(number_order=i+1)
            amount, currency = amount_n_currency_section(number_order=i+1)
            
            direction, reason = direction_n_reason_section(number_order=i+1)

            swift_def, swift_ben_def, iban_def = None, None, None

            df, md5 = load_beneficiaries_db(UBS_PAYMENTS_DB_SSI_ABS_PATH, PAYMENTS_BENECIFIARY_SHEET_NAME, PAYMENTS_BENEFICIARY_COLUMNS)
            row = find_beneficiary_by_ctpy_ccy_n_type(df, md5, ctpy, market, currency)
            
            print(row)
            
            if row is not None :
                swift_def, _, swift_ben_def, iban_def = row
            
            swift_bank, iban, swift_benif = swift_iban_section(swift_def, iban_def, swift_ben_def, number_order=i+1)

            security = (product, trade_ref, reason, acc, ctpy, direction, amount, currency, date, "NaN", swift_bank, iban, swift_benif)
            securities.append(security)
            """
    return securities


def fund_ctpy_n_acc_section (
        
        fundations : Optional[List[str]] = None,
        counterparties : Optional[Dict] = None,
        accounts : Optional[List[str]] = None,

        number_order : int = 1
        
    ) :
    """
    Docstring for fund_ctpy_n_acc_section
    """
    fundations = PAYMENTS_FUNDS if fundations is None else fundations

    counterparties_dict = PAYMENTS_COUNTERPARTIES if counterparties is None else counterparties
    counterparties = list(counterparties_dict.keys())

    accounts = PAYMENTS_ACCOUNTS if accounts is None else accounts

    key_fundation = f"Settlement_Security_{number_order}_fundation"
    key_counterparty = f"Settlement_Security_{number_order}_counterparty"
    key_account = f"Settlement_Security_{number_order}_account"

    fund, ctpy, acc = general_payment_fields(fundations, counterparties, accounts, number_order, key_fundation, key_counterparty, key_account)

    return fund, ctpy, acc



def process_securities_section (securities) :
    """
    Docstring for process_securities_section
    
    :param securities: Description
    """
    st.warning("Hello World")

    return None