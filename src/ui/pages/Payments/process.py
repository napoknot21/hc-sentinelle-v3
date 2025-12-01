from __future__ import annotations

import re
import streamlit as st
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h3, center_h5, left_h5
from src.ui.components.selector import number_of_payments_selector, date_selector
from src.ui.components.input import (
    general_payment_fields, type_market_fields, amount_currency_fields,
    name_reference_bank_fields, bank_benificiary_fields, iban_field,
    extra_options_fields
)

from src.core.data.payments import find_beneficiary_by_ctpy_ccy_n_type, export_payments_to_email

from src.config.parameters import PAYMENTS_FUNDS, PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_TYPES_MARKET, PAYMENTS_REFERENCES_CTPY, PAYMENTS_ACCOUNTS


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
    
    st.button("Process Payments", on_click=process_payements_section(payments, email, book))

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
    payments = []

    for i, column in enumerate(cols) :

        with column :

            center_h5(f"Payment {i+1}")

            fund, ctpy, acc = input_payment_section(number_order=i+1)
            type, market = type_payment_section(number_order=i+1)
            date, amount, currency = date_n_amount_section(number_order=i+1)
            name, reference = statement_reference_setion(ctpy, type, number_order=i+1)

            swift_def, benif_def, swift_ben_def, iban_def = None, None, None, None

            row = find_beneficiary_by_ctpy_ccy_n_type(None, None, ctpy, market, currency)

            if row is not None :
                swift_def, benif_def, swift_ben_def, iban_def = row

            bank, swift_bank, benif, swift_benif = bank_benificiary_section(ctpy, swift_def, benif_def, swift_ben_def, order_number=i+1)
            
            iban = iban_section(iban_def, order_number=i+1)
            
            payment = (fund, ctpy, acc, type, market, date, amount, currency, name, reference, bank, swift_bank, benif, swift_benif, iban)
    
            payments.append(payment)

    print(payments)

    return payments


def input_payment_section (

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
        
        counterparty : Optional[str] = None,
        
        swift_bank : Optional[str] = None,
        benif : Optional[str] = None,
        swift_benif : Optional[str] = None,

        counterparties : Optional[Dict] = None,
        order_number : int = 1
    
    ) :
    """

    """
    counterparties = PAYMENTS_COUNTERPARTIES if counterparties is None else counterparties
    bank_name = counterparties.get(counterparty).get("bank")

    bank, swift_bank, benif, swift_benif = bank_benificiary_fields(bank_name, swift_bank, benif, swift_benif, order_number)

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
        
        bo = export_payments_to_email(payments)
        st.info("Running and Proceding")
    
