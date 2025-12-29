from __future__ import annotations

import polars as pl
import datetime as dt
import streamlit as st

from typing import Optional, List, Dict, Tuple


def general_payment_fields (
        
        fundations : Optional[List[str]] = None,
        counterparties : Optional[List[str]] = None,
        account_numbers : Optional[List[str]] = None,

        number_order : int = 1,

        key_fundation : Optional[str] = None,
        key_counterparty : Optional[str] = None,
        key_account : Optional[str] = None,

        fund_title : Optional[str] = None,
        ctpy_title : Optional[str] = None,
        acct_title : Optional[str] = None,

    ) :
    """
    
    """
    key_fundation = f"Payment_process_{number_order}_fundation" if key_fundation is None else key_fundation
    key_counterparty = f"Payment_process_{number_order}_counterparty" if key_counterparty is None else key_counterparty
    key_account = f"Payment_process_{number_order}_account" if key_account is None else key_account

    fund_title = "Fundation Name" if fund_title is None else fund_title
    ctpy_title = "Counterparty" if ctpy_title is None else ctpy_title
    acct_title = "Account Number Payment" if acct_title is None else acct_title

    if fundations is not None :
        fundation = st.selectbox(fund_title, options=fundations, key=key_fundation)
    
    if counterparties is not None :
        counterparty = st.selectbox(ctpy_title, options=counterparties, key=key_counterparty)
    
    if account_numbers is not None :
        account = st.selectbox(acct_title, options=account_numbers, key=key_account)

    return fundation, counterparty, account


def type_market_fields (
        
        type_market : Optional[Dict] = None,
        types : Optional[List[str]] = None,

        number_order : int = 1,

    ) :
    """
    
    """
    col1, col2 = st.columns(2)

    with col1 :
        type = st.selectbox("Type", options=types, key=f"Type_market_{number_order}_type")

    with col2 :
        
        markets = type_market.get(type)
        market = st.selectbox("Market", options=markets, key=f"Type_market_{number_order}_market")

    return type, market


def amount_currency_fields (
        
        currencies : Optional[List] = None,
        number_order : int = 1,

        key_amount : Optional[str] = None,
        key_currency : Optional[str] = None,

        amount_title : str = "Amount",
        currency_title : str = "Currency"

    ) :
    """
    
    """
    key_amount = f"amount_payment_{number_order}" if key_amount is None else key_amount
    key_currency = f"currency_payement_{number_order}" if key_currency is None else key_currency

    col1, col2 = st.columns(2)

    with col1 :

        amount = st.number_input(amount_title, key=key_amount)

        if amount <= 0 :
            st.warning("Warning : Amount under or equals to 0...")

    with col2 :
        currency = st.selectbox(currency_title, options=currencies, key=key_currency)

    return amount, currency


def name_reference_bank_fields (
        
        default_name : Optional[str] = None,
        default_reference : Optional[str] = None,

        key_name : Optional[str] = None,
        key_ref : Optional[str] = None,

        number_order : int = 1


    ) -> Tuple[str, str]:
    """
    
    """
    key_name = f"name_ref_bank_{number_order}" if key_name is None else key_name
    key_ref = f"ref_name_bank_{number_order}" if key_ref is None else key_ref

    # --- Keys to remember the last defaults used ---
    name_default_key = f"{key_name}_default"
    ref_default_key = f"{key_ref}_default"

    last_default_name = st.session_state.get(name_default_key)
    last_default_ref = st.session_state.get(ref_default_key)

    # If the default changed (e.g. new counterparty/type), reset the field
    if last_default_name != default_name :

        st.session_state[key_name] = default_name
        st.session_state[name_default_key] = default_name
    
    if last_default_ref != default_reference :

        st.session_state[key_ref] = default_reference
        st.session_state[ref_default_key] = default_reference

    # ----- Now render the widgets (value comes from session_state) -----

    col1, col2 = st.columns(2)

    with col1 :
        name = st.text_input("Name on Bank Statement", value=default_name, key=f"name_ref_bank_{number_order}")

    with col2 :
        reference = st.text_input("Reference for Bank", value=default_reference, key=f"ref_name_bank_{number_order}")

    return name, reference


def bank_benificiary_fields (
        
        bank_name : Optional[str] = None,

        swift_bank_default : Optional[str] = None,
        benif_default : Optional[str] = None,
        swift_benif_default : Optional[str] = None,


        number_order : int = 1,

    ) :
    """
    
    """
    # --- Keys for widgets ---
    key_bank       = f"bank_{number_order}"
    key_benif      = f"benificiary_bank_{number_order}"
    key_swift      = f"swift_code_bank_{number_order}"
    key_swift_ben  = f"benificiary_swift_code_{number_order}"

    # --- Keys to remember last defaults ---
    key_bank_def      = f"{key_bank}_default"
    key_benif_def     = f"{key_benif}_default"
    key_swift_def     = f"{key_swift}_default"
    key_swift_ben_def = f"{key_swift_ben}_default"

    # ---------- BANK NAME ----------
    last_bank_default = st.session_state.get(key_bank_def)

    if last_bank_default != bank_name :
        st.session_state[key_bank] = bank_name
   
    # ---------- BENEFICIARY BANK ----------
    last_benif_default = st.session_state.get(key_benif_def)

    if last_benif_default != benif_default :
        st.session_state[key_benif] = benif_default

    # ---------- SWIFT BANK ----------
    last_swift_default = st.session_state.get(key_swift_def)

    if last_swift_default != swift_bank_default :
        st.session_state[key_swift] = swift_bank_default
       
    last_swift_ben_default = st.session_state.get(key_swift_ben_def)

    if last_swift_ben_default != swift_benif_default:
        st.session_state[key_swift_ben] = swift_benif_default
       
    # ---------- RENDER WIDGETS ----------
    col1, col2 = st.columns(2)

    with col1:
        bank = st.text_input("Bank", key=f"bank_{number_order}")
        benif = st.text_input("Beneficiary Bank", key=key_benif)

    with col2:
        swift = st.text_input("Swift-Code Bank", key=key_swift)
        swift_benif = st.text_input("Beneficiary Swift-Code", key=key_swift_ben)

    return bank, swift, benif, swift_benif


def iban_field (
        
        iban_default: Optional[str] = None,
        max_length: int = 35,
        number_order: int = 1,
    ) :

    key_iban = f"iban_{number_order}"
    key_default = f"{key_iban}_default"

    # If the default changed → update session_state
    last_default = st.session_state.get(key_default)

    if iban_default is not None and last_default != iban_default:
        st.session_state[key_iban] = iban_default


    # Render widget (session_state provides the value)
    res = st.text_input("IBAN", key=key_iban)

    return res



def extra_options_fields (
        

    ) :
    """
    
    """

    email = st.checkbox("Create Emails (with PDF files)")
    book = st.checkbox("Book payments")

    return email, book


def check_inputs (
        


    ) :
    """
    
    """

    return True



