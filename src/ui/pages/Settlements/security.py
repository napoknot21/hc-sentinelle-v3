from __future__ import annotations

import os
import streamlit as st

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_items_selector, date_selector
from src.ui.components.input import (
    general_payment_fields, amount_currency_fields, type_return_fields, ubs_broker_fields,
    product_n_trade_ref_fields, dates_sections
)

from src.core.data.payments import (
    find_beneficiary_by_ctpy_ccy_n_type, process_excel_to_pdf, process_payments_to_excel, 
    create_payement_email, load_beneficiaries_db
)

from src.config.parameters import (
    PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_BOOKS,
    PAYMENTS_DIRECTIONS, PAYMENTS_ACCOUNTS, PAYMENTS_BENEFICIARY_COLUMNS, PAYMENTS_BENECIFIARY_SHEET_NAME,
    UBS_PAYMENTS_ACCOUNTS
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
            trade_ref = reference_security_section(number_order=i+1)

            t_date, s_date = trade_n_settlement_dates_section(number_order=i+1)
            
            quantity, currency = ccy_n_quantity_section(number_order=i+1)
            """
            
            _, market = type_market_section(number_order=i+1)
            
            date = value_date_section(number_order=i+1)
            
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

    accounts = UBS_PAYMENTS_ACCOUNTS if accounts is None else accounts

    key_fundation = f"Settlement_Security_{number_order}_fundation"
    key_counterparty = f"Settlement_Security_{number_order}_counterparty"
    #key_account = f"Settlement_Security_{number_order}_account"

    fund, ctpy, acc = general_payment_fields(fundations, counterparties, None, number_order, key_fundation, key_counterparty)
    acc = accounts.get(fund, None)

    return fund, ctpy, acc



def process_securities_section (securities) :
    """
    Docstring for process_securities_section
    
    :param securities: Description
    """
    st.warning("Hello World")

    return None


def reference_security_section (
        
        number_order : int = 1,
    
        ref_label : Optional[str] = None,
        ref_key : Optional[str] = None,

    ) :
    """
    
    """

    ref_label = "Reference" if ref_label is None else ref_label
    ref_key = f"Settlement_Security_{number_order}_reference" if ref_key is None else ref_key

    reference, _ = product_n_trade_ref_fields(number_order, None, ref_key, None, ref_label)

    return reference


def trade_n_settlement_dates_section (
        
        number_order : int = 1,

        t_date_key : Optional[str] = None,
        t_date_label : Optional[str] = None,

        s_date_key : Optional[str] = None,
        s_date_label : Optional[str] = None,

    ) :
    """
    
    """
    t_date_key = f"Settlement_Security_{number_order}_trade_date" if t_date_key is None else t_date_key
    t_date_label = "Trade Date" if t_date_label is None else t_date_label

    s_date_key =  f"Settlement_Security_{number_order}_settlement_date" if s_date_key is None else s_date_key
    s_date_label = "Settlement Date" if s_date_label is None else s_date_label

    col1, col2 = st.columns(2)

    with col1 :
        t_date = date_selector(t_date_label, key=t_date_key)
        
    with col2 :
        s_date =  date_selector(s_date_label, key=s_date_key)

    return t_date, s_date



def ccy_n_quantity_section (
        
        currencies : Optional[List[str]] = None,
        
        number_order : int = 1,
    
        quant_label : Optional[str] = None,
        ccy_label : Optional[str] = None,

        quant_key : Optional[str] = None,
        ccy_key : Optional[str] = None,
    ) :
    """
    Docstring for amount_n_currency_section
    
    :param number_order: Description
    :type number_order: int
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    quant_label = "Quantity" if quant_label is None else quant_label
    quant_key = f"Settlement_Security_{number_order}_quantity" if quant_key is None else quant_key

    ccy_label = "Currency" if ccy_label is None else ccy_label
    ccy_key = f"Settlement_Security_{number_order}_currency" if ccy_key is None else ccy_key

    amount, currency = amount_currency_fields(currencies, number_order, quant_key, ccy_key, quant_label, ccy_label)

    return amount, currency