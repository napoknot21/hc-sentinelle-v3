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
    PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_TYPES_MARKET,
    PAYMENTS_REFERENCES_CTPY, PAYMENTS_ACCOUNTS, PAYMENTS_BENEFICIARY_COLUMNS, PAYMENTS_BENECIFIARY_SHEET_NAME
)
from src.config.paths import UBS_PAYMENTS_DB_SSI_ABS_PATH

from src.utils.formatters import date_to_str


def colleteral_management (default_value : int = 1) :
    """
    Docstring for colleteral_management
    """
    center_h2("Collateral Management")
    nb_collateral = nb_of_payments_section(default_value)

    collaterals = input_collateral_section(nb_payments=nb_collateral)

    st.write('')
    left_h5("Export option")

    if st.button("Process Cash Collateral") :
        st.warning("Hello World")

    return None


# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1, max_value : int = 4) :
    """
    
    """
    nb_payments = number_of_items_selector("Select number of Cash Collateral", default_value, max_value)

    return nb_payments



def input_collateral_section (nb_payments : int = 1) :
    """
    Docstring for payment_section
    
    :param nb_payments: Description
    :type nb_payments: int
    """
    cols = st.columns(nb_payments)
    collaterals = []

    for i, col in enumerate(cols) :

        with col :

            center_h5(f"Collateral {i+1}")
            
            fund, ctpy, acc = fund_ctpy_n_acc_section(number_order=i+1)
            type_collateral = type_return_section(number_order=i+1)

            amount, currency = amount_n_currency_section(number_order=i+1)
            t_date, v_date = value_date_section(number_order=i+1)
            
            swift_def, swift_ben_def, iban_def = None, None, None
            
            df, md5 = load_beneficiaries_db(UBS_PAYMENTS_DB_SSI_ABS_PATH, PAYMENTS_BENECIFIARY_SHEET_NAME, PAYMENTS_BENEFICIARY_COLUMNS)
            row = find_beneficiary_by_ctpy_ccy_n_type(df, md5, ctpy, None, currency)
            st.warning(row)

            if row is not None :
                swift_def, _, swift_ben_def, iban_def = row
            
            swift_bank, iban, swift_benif = swift_iban_section(swift_def, iban_def, swift_ben_def, number_order=i+1)
            
            
            collateral = (type_collateral, acc, fund, ctpy, None, currency, amount, t_date, v_date, swift_bank, iban, swift_benif)
            collaterals.append(collateral)

    return collaterals


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

    key_fundation = f"Settlement_Collateral_{number_order}_fundation"
    key_counterparty = f"Settlement_Collateral_{number_order}_counterparty"
    key_account = f"Settlement_Collateral_{number_order}_account"

    fund, ctpy, acc = general_payment_fields(fundations, counterparties, accounts, number_order, key_fundation, key_counterparty, key_account)

    return fund, ctpy, acc


def type_return_section (
        
        flows : Optional[List[str]] = None,
        returns : Optional[List[str]] = None,

        number_order : int = 1,

        type_name : Optional[str] = "Cash Collateral"

    ) :
    """
    Docstring for type_return_section
    """
    flows = ["Given", "Receive"] if flows is None else flows
    returns = ["Yes", "No"] if returns is None else returns

    flow, ret = type_return_fields(flows, returns, number_order=number_order)

    type_cash = type_name + " " + flow
    
    if ret is "Yes" :
        type_cash += " - Return" 

    return type_cash


def value_date_section (number_order : int = 1, format : str = "%d.%m.%Y") :
    """
    Docstring for value_date_section
    """
    key_date_t = f"Settlement_Collateral_{number_order}_t_date"
    key_date_v = f"Settlement_Collateral_{number_order}_v_date"
    
    col1, col2 = st.columns(2) 
    
    with col1 :
        t_date = date_selector("Termination Date", key=key_date_t)
    
    with col2 :
        v_date = date_selector("Valuation Date", key=key_date_v)

    t_date = date_to_str(t_date, format=format)
    v_date = date_to_str(v_date, format=format)

    return t_date, v_date


def amount_n_currency_section (currencies : Optional[List[str]] = None, number_order : int = 1) :
    """
    Docstring for amount_n_currency_section
    
    :param number_order: Description
    :type number_order: int
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    key_amount = f"Settlement_Collateral_{number_order}_amount"
    key_currency = f"Settlement_Collateral_{number_order}_currency"

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
