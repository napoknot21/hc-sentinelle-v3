from __future__ import annotations

import os
import streamlit as st

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_items_selector, date_selector
from src.ui.components.input import (
    general_payment_fields, type_market_setlement_fields, amount_currency_fields,
    ubs_broker_fields, bank_benificiary_fields, iban_field,
    extra_options_fields, direction_flow_fields, product_n_trade_ref_fields
)

from src.core.data.payments import (
    find_beneficiary_by_ctpy_ccy_n_type, process_excel_to_pdf, process_payments_to_excel, 
    create_payement_email, load_beneficiaries_db
)

from src.config.paths import UBS_PAYMENTS_DB_SSI_ABS_PATH
from src.config.parameters import (
    PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_TYPES_MARKET, UBS_PAYMENTS_TYPES, UBS_PAYMENTS_MARKET,
    PAYMENTS_REFERENCES_CTPY, PAYMENTS_ACCOUNTS, PAYMENTS_DIRECTIONS, PAYMENTS_BENEFICIARY_COLUMNS, PAYMENTS_BENECIFIARY_SHEET_NAME
)

from src.utils.data_io import convert_ubs_instruction_payments_to_excel, export_excel_to_pdf


def payments_process (default_value : int = 1) :
    """
    Docstring for payments_process
    """
    center_h2("OTC Payments")
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

            center_h5(f"Settlement {i+1}")
            
            _, ctpy, acc = fund_ctpy_n_acc_section(number_order=i+1)
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

            payment = (product, trade_ref, reason, acc, ctpy, direction, amount, currency, date, "NaN", swift_bank, iban, swift_benif)
            payments.append(payment)

    return payments


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

    key_fundation = f"UBS_OTC_Payment_{number_order}_fundation"
    key_counterparty = f"UBS_OTC_Payment_{number_order}_counterparty"
    key_account = f"UBS_OTC_Payment_{number_order}_account"

    fund, ctpy, acc = general_payment_fields(fundations, counterparties, accounts, number_order, key_fundation, key_counterparty, key_account)

    return fund, ctpy, acc


def product_n_trade_ref_section (

        number_order : int = 1,
    ) :
    """
    Docstring for product_n_trade_ref_section
    """
    product, trade_ref = product_n_trade_ref_fields(number_order)

    return product, trade_ref


def type_market_section (

        types : Optional[List[str]] = None,
        markets : Optional[List[str]] = None,

        number_order : int = 1,

    ) :
    """
    Docstring for type_market_section
    """
    types = UBS_PAYMENTS_TYPES if types is None else types
    markets = UBS_PAYMENTS_MARKET if markets is None else markets

    type, market = type_market_setlement_fields(types, markets, number_order=number_order)

    return type, market


def direction_n_reason_section (
        
        directions : Optional[List] = None,
        number_order : int = 1,
    ) :
    """
    Docstring for product_n_trade_ref_section
    """
    directions = PAYMENTS_DIRECTIONS if directions is None else directions

    key_direction = f"UBS_OTC_Payment_{number_order}_direction" 
    key_reason = f"UBS_OTC_Payment_{number_order}_reason" 

    direction, reason = direction_flow_fields(directions, None, key_direction, key_reason, number_order=number_order)

    return direction, reason


def value_date_section (number_order : int = 1) :
    """
    Docstring for value_date_section
    """
    key_date = f"UBS_OTC_Payment_{number_order}_date"
    date = date_selector("Value Date", key=key_date)

    return date


def amount_n_currency_section (currencies :  Optional[List[str]] = None, number_order : int = 1) :
    """
    Docstring for amount_n_currency_section
    
    :param number_order: Description
    :type number_order: int
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    key_amount = f"UBS_OTC_Payment_{number_order}_amount"
    key_currency = f"UBS_OTC_Payment_{number_order}_currency"

    amount, currency = amount_currency_fields(currencies, number_order, key_amount, key_currency)

    return amount, currency


def swift_iban_section (
        
        swift_code : Optional[str] = None,
        iban : Optional[str] = None,
        swift_benef : Optional[str] = None,

        number_order : int = 1,

    ) :
    """
    Docstring for swift_iban_section
    """
    bic, iban, bic_ben = ubs_broker_fields(swift_code, iban, swift_benef, number_order=number_order)
    
    return bic, iban, bic_ben


# Process and file creation

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


