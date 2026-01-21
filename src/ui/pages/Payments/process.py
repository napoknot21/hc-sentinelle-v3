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

# ----------- Main ------------

def process (default_value : int = 1) :
    """
    Main function that displays the Payments Process page
    """
    center_h2("Process Payments")
    nb_payments = nb_of_payments_section(default_value)

    payments = payments_section(nb_payments)

    st.write('')
    left_h5("Export Option")

    email, book = extra_options_section()
    
    if st.button("Process Payments") :
        process_payements_section(payments, email, book)

    return None


# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_items_selector(min_value=default_value)

    return nb_payments


# ----------- Input Section -----------

def payments_section (nb_payments : int = 1) :
    """
    
    """
    cols = st.columns(nb_payments)
    payments = []

    for i, column in enumerate(cols) :

        with column :

            payment = input_payment_section(i)
            payments.append(payment)

            print(payments)

    return payments


# Payment object / Full section
def input_payment_section (i : int = 0) :
    """
    Docstring for input_payment_section
    """

    center_h5(f"Payment {i+1}")

    fund, ctpy, acc = fund_ctpy_n_acc_section(number_order=i+1)
    type, market = type_payment_section(number_order=i+1)
    date, amount, currency = date_n_amount_section(number_order=i+1)
    name, reference = statement_reference_setion(ctpy, type, number_order=i+1)

    bank_def, swift_def, benif_def, swift_ben_def, iban_def = None, None, None, None, None

    row = find_beneficiary_by_ctpy_ccy_n_type(None, None, ctpy, market, currency)

    if row is not None :
        bank_def, swift_def, benif_def, swift_ben_def, iban_def = row

    bank, swift_bank, benif, swift_benif  = bank_benificiary_section(bank_def, swift_def, benif_def, swift_ben_def, order_number=i+1)

    iban = iban_section(iban_def, order_number=i+1)
    
    # Final payement "object"
    payment = (fund, acc, currency, amount, date, "SHA", bank, reference, iban, swift_bank, benif, swift_benif, name)
    
    return payment


def fund_ctpy_n_acc_section (

        fundations : Optional[List[str]] = None,
        counterparties : Optional[Dict] = None,
        accounts : Optional[List[str]] = None,

        number_order : int = 1,

    ) :
    """
    
    """
    fundations = PAYMENTS_FUNDS if fundations is None else fundations
    accounts = PAYMENTS_ACCOUNTS if accounts is None else accounts

    counterparties_dict = PAYMENTS_COUNTERPARTIES if counterparties is None else counterparties
    counterparties = list(counterparties_dict.keys())

    fundation, counterparty, account = general_payment_fields(fundations, counterparties, accounts, number_order)
    
    return fundation, counterparty, account


def type_payment_section (
        
        type_market : Optional[Dict] = None,
        number_order : int = 1,

    ) :
    """
    
    """
    type_market = PAYMENTS_TYPES_MARKET if type_market is None else type_market

    types = list(type_market.keys())
    type, market = type_market_fields(type_market, types, number_order)

    return type, market


def date_n_amount_section (
        
        currencies : Optional[List] = None,
        number_order : int = 1,

    ) -> Tuple[str, float, str] :
    """
    
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    date = date_selector("Value Date", key=f"value_date_{number_order}")
    amount, currency = amount_currency_fields(currencies, number_order=number_order)

    return date, amount, currency


def statement_reference_setion (
        
        counterparty : Optional[str] = None,
        type : Optional[str] = None,

        counterparties : Optional[Dict] = None,
        references : Optional[Dict] = None,

        number_order: int = 1

    ) -> Tuple[str, str] :
    """
    
    """
    counterparties = PAYMENTS_COUNTERPARTIES if counterparties is None else counterparties
    references = PAYMENTS_REFERENCES_CTPY if references is None else references

    type = list(PAYMENTS_TYPES_MARKET.keys())[0] if type is None else type
    ctpy_value = counterparties.get(counterparty).get("initials")

    default_name = ctpy_value + " " + type
    default_reference = references.get(type).get(counterparty) # could be Null

    name, reference = name_reference_bank_fields(default_name, default_reference, number_order=number_order) 

    return name, reference


def bank_benificiary_section (
        
        bank_def : Optional[str] = None,
        swift_bank_def : Optional[str] = None,
        benif_def : Optional[str] = None,
        swift_benif_def : Optional[str] = None,

        order_number : int = 1
    
    ) :
    """

    """
    bank, swift_bank, benif, swift_benif = bank_benificiary_fields(bank_def, swift_bank_def, benif_def, swift_benif_def, order_number)

    return bank, swift_bank, benif, swift_benif


def iban_section (
        
        iban_default : Optional[str] = None,
        max_length : int = 35,
        order_number : int = 1,

    ) :
    """
    
    """

    iban = iban_field(iban_default, max_length, order_number)

    return iban


# ----------- Export options (footer) -----------

def extra_options_section () :
    """
    
    """

    email, book = extra_options_fields()

    return email, book


def process_payements_section (
        
        payments : Optional[List] = None,

        email : bool = True,
        book : bool = True,

    ) :
    """
    
    """
    if email is False and book is False :
        
        st.warning("You need to choose at least One option !")
        return None 

    if email :
        
        excel_paths = process_payments_to_excel(payments)
        pdf_files = process_excel_to_pdf(excel_paths)

        print(f"\n[*] Converted {pdf_files}")

        status = create_payement_email(files_attached=pdf_files)

        if status.get("success") :
            
            path = status.get("path")

            print(f"\n[+] Mesage created and stored in {path}")
            st.info("Email successfully created. Ready to download")

            with open(path, "rb") as f :
                file_bytes = f.read()

            st.download_button(
                "Download Payment instruction",
                data=file_bytes,
                file_name=os.path.basename(status.get("path")),
                mime="application/octet-stream",  # ou "application/vnd.ms-outlook" si .msg
            )

        else :
            
            msg = status.get("message")
            st.error(f"{msg}")
            
    return None

