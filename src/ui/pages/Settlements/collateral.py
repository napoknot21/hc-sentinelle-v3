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
from src.utils.data_io import convert_ubs_collateral_management_to_excel, export_excel_to_pdf


def colleteral_management (default_value : int = 1) :
    """
    Docstring for colleteral_management
    """
    center_h2("Collateral Management")
    nb_collateral = nb_of_payments_section(default_value)

    collaterals, bookers = input_collateral_section(nb_payments=nb_collateral)

    st.write('')
    left_h5("Export option")

    if st.button("Process Securities") :
        process_collaterals_section(collaterals)

    return None


# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1, max_value : int = 4) :
    """
    
    """
    nb_payments = number_of_items_selector(

        "Select number of Cash Collateral",
        default_value,
        max_value
        
    )

    return nb_payments



def input_collateral_section (nb_payments : int = 1) :
    """
    Docstring for payment_section
    
    :param nb_payments: Description
    :type nb_payments: int
    """
    cols = st.columns(nb_payments)

    collaterals = []
    bookers = []

    for i, col in enumerate(cols) :

        with col :

            center_h5(f"Collateral {i+1}")
            
            fund, ctpy, acc = fund_ctpy_n_acc_section(number_order=i+1)
            direction, type_collateral = type_return_section(number_order=i+1)

            amount, currency = amount_n_currency_section(number_order=i+1)
            t_date, v_date = value_date_section(number_order=i+1)
            
            swift_def, swift_ben_def, iban_def = None, None, None
            
            df, md5 = load_beneficiaries_db(UBS_PAYMENTS_DB_SSI_ABS_PATH, PAYMENTS_BENECIFIARY_SHEET_NAME, PAYMENTS_BENEFICIARY_COLUMNS)
            row = find_beneficiary_by_ctpy_ccy_n_type(df, md5, ctpy, "Collateral Management", currency)

            if row is not None :
                _, swift_def, _, swift_ben_def, iban_def = row
            
            swift_bank, iban, swift_benif = swift_iban_section(swift_def, iban_def, swift_ben_def, number_order=i+1)
            
            book = book_section(number_order=i+1)

            collateral = (type_collateral, acc, fund, ctpy, None, currency, amount, t_date, v_date, swift_bank, iban, swift_benif)
            booked = (amount, direction, v_date, book)
            
            if book is not None :
                bookers.append(booked)
            
            collaterals.append(collateral)

    return collaterals, bookers


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
    flows = PAYMENTS_DIRECTIONS if flows is None else flows
    returns = ["Yes", "No"] if returns is None else returns

    flow, ret = type_return_fields(flows, returns, number_order=number_order)

    type_cash = type_name + " " + ("Give" if flow == "Pay" else flow)
    
    if ret == "Yes" :
        type_cash += " - Return" 

    return flow, type_cash


def value_date_section (number_order : int = 1, format : str = "%d.%m.%Y") :
    """
    Docstring for value_date_section
    """
    key_date_t = f"Settlement_Collateral_{number_order}_t_date"
    key_date_v = f"Settlement_Collateral_{number_order}_v_date"
    
    col1, col2 = st.columns(2) 
    
    with col1 :
        t_date = date_selector("Trade Date", key=key_date_t)
    
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

        key_bic : Optional[str] = None,
        key_iban : Optional[str] = None,
        key_bic_ben :Optional[str] = None,

    ) :
    """
    Docstring for swift_iban_section
    """
    key_bic = f"Settlement_Collateral_{number_order}_bic" if key_bic is None else key_bic
    key_iban = f"Settlement_Collateral_{number_order}_iban" if key_iban is None else key_iban
    key_bic_ben = f"Settlement_Collateral_{number_order}_bic_ben" if key_bic_ben is None else key_bic_ben

    bic, iban, bic_ben = ubs_broker_fields(
        swift_code, iban, swift_benef, number_order=number_order,
        key_bic=key_bic, key_iban=key_iban, key_bic_ben=key_bic_ben
    )
    
    return bic, iban, bic_ben


def book_section (
        
        books : Optional[List[str]] = None,

        number_order : int = 1,

        key_check : Optional[str] = None,
        key_book : Optional[str] = None,
        
    ) :
    """
    
    """
    books = PAYMENTS_BOOKS if books is None else books
    
    key_check = f"Settlement_Collateral_{number_order}_check" if key_check is None else key_check
    key_book = f"Settlement_Collateral_{number_order}_book" if key_book is None else key_book

    book = None
    
    if st.checkbox("Book Option", key=key_check) :
        book = st.selectbox("Book", options=books, key=key_book)

    return book


def process_collaterals_section (
        
        collaterals : Optional[List] = None,

    ) :
    """
    Docstring for process_payements_section
    
    :param payments: Description
    :type payments: Optional[List]
    """
    response = convert_ubs_collateral_management_to_excel(collaterals)
    status = response["success"]

    st.write(response)
    if status is True :

        filename, _ = os.path.splitext(os.path.basename(response.get("path")))
        pdf_status = export_excel_to_pdf(response.get("path"), filename + ".pdf", orientation=1)
        
        if pdf_status.get("success") :

            st.warning(f"{pdf_status["message"]}")
            st.warning(f"Successfully at {pdf_status.get("path")}")
            
            email = create_payement_email(files_attached=[pdf_status.get("path")])

            if email.get("success") :
                
                path = email.get("path")

                print(f"\n[+] Mesage created and stored in {path}")
                st.info("Email successfully created. Ready to download")
                
                with open(email.get("path"), "rb") as f :
                    file_bytes = f.read()

                st.download_button(
                    "Download Payment instruction",
                    data=file_bytes,
                    file_name=os.path.basename(email.get("path")),
                    mime="application/octet-stream",  # ou "application/vnd.ms-outlook" si .msg
                )
        
        else  :

            st.error("[-] Error during Payment generation")

    else :
        
        st.error(f"{response["message"]}")

    return None
