from __future__ import annotations

import os
import streamlit as st
import polars as pl

from typing import List, Optional, Dict, Tuple

from src.ui.components.text import center_h2, center_h5, left_h5
from src.ui.components.selector import number_of_items_selector, date_selector
from src.ui.components.input import (
    general_payment_fields, type_market_fields, amount_currency_fields,
    name_reference_bank_fields, bank_benificiary_fields, iban_field,
    extra_options_fields
)
from src.utils.data_io import export_dataframe_to_excel, export_excel_to_pdf
from src.core.data.payments import (
    find_beneficiary_by_ctpy_ccy_n_type, process_excel_to_pdf, process_payments_to_excel, 
    create_payement_email, create_settlement_fx_payment_excel
)
from src.ui.pages.Settlements.payments import type_market_section

from src.config.parameters import (
    PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, UBS_PAYMENTS_TYPES,
    UBS_PAYMENTS_MARKET, UBS_PAYMENTS_ACCOUNTS, PAYMENTS_DIRECTIONS, PAYMENTS_BENEFICIARY_COLUMNS, 
    PAYMENTS_BENECIFIARY_SHEET_NAME, UBS_PAYMENTS_FUNDS, UBS_PAYMENTS_DIRECTIONS
)
from src.config.paths import PAYMENTS_DIR_ABS_PATH
from src.utils.formatters import date_to_str, str_to_date


def forex (default_value : int = 1) :
    """
    Docstring for forex
    """
    center_h2("FX Payments")

    nb_payments = nb_of_payments_section(default_value)
    payments = fx_payments_section(nb_payments)

    if st.button("Export FX Payments") :
        export_fx_payment_section(payments)

    return None



# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_items_selector(min_value=default_value)

    return nb_payments


# ----------- Input Section -----------

def fx_payments_section (nb_payments : int) :
    """
    
    """
    payments = []
    cols = st.columns(nb_payments)

    for i, column in enumerate(cols) :

        with column :

            payment = input_fx_payment(order_number=i+1)
            payments.append(payment)

            print(payment)

    return payments


def input_fx_payment (order_number : int = 1) :
    """
    Docstring for input_fx_payment
    
    :param order_number: Description
    :type order_number: int
    """
    center_h5(f"FX Payment {order_number}")

    _, ctpy, acc = fund_ctpy_n_acc_section(number_order=order_number+1)

    direction = direction_section(number_order=order_number+1)
    amount, currency = amount_n_currency_section(number_order=order_number+1)

    fx_rate = fx_rate_section(number_order=order_number+1)
    
    sett, ctpy_ccy = counter_settlement_section(number_order=order_number+1)
    t_date, m_date = value_date_section(number_order=order_number+1)

    bic = bic_code_section(number_order=order_number+1)

    payment = (acc, None, direction, currency, amount, ctpy_ccy, fx_rate, sett, t_date, m_date, bic)

    return payment


def fund_ctpy_n_acc_section (
        
        fundations : Optional[List[str]] = None,
        counterparties : Optional[Dict] = None,
        accounts : Optional[List[str]] = None,

        number_order : int = 1
        
    ) :
    """
    Docstring for fund_ctpy_n_acc_section
    """
    fundations = UBS_PAYMENTS_FUNDS if fundations is None else fundations

    counterparties_dict = PAYMENTS_COUNTERPARTIES if counterparties is None else counterparties
    counterparties = list(counterparties_dict.keys())

    accounts = UBS_PAYMENTS_ACCOUNTS if accounts is None else accounts

    key_fundation = f"UBS_FX_Payment_{number_order}_fundation"
    key_counterparty = f"UBS_FX_Payment_{number_order}_counterparty"
    key_account = f"UBS_FX_Payment_{number_order}_account"

    fund, ctpy, acc = general_payment_fields(fundations, counterparties, accounts, number_order, key_fundation, key_counterparty, key_account)

    return fund, ctpy, acc


def direction_section (directions : Optional[List[str] | Dict] = None, number_order : int = 1) :
    """
    Docstring for direction_section
    
    :param number_order: Description
    :type number_order: int
    """
    directions = UBS_PAYMENTS_DIRECTIONS if directions is None else directions
    key_direction = f"UBS_FX_Payment_{number_order}_direction"

    direction = st.selectbox("Direction", directions, key=key_direction)

    return direction


def amount_n_currency_section (currencies :  Optional[List[str]] = None, number_order : int = 1) :
    """
    Docstring for amount_n_currency_section
    
    :param number_order: Description
    :type number_order: int
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    key_amount = f"UBS_FX_Payment_{number_order}_amount"
    key_currency = f"UBS_FX_Payment_{number_order}_currency"

    amount, currency = amount_currency_fields(currencies, number_order, key_amount, key_currency, "Nominal Amount")

    return amount, currency


def fx_rate_section (number_order : int = 1) :
    """
    Docstring for fx_rate_section
    
    :param number_order: Description
    :type number_order: int
    """
    key_fx_rate = f"UBS_FX_Payment_{number_order}_fx_rate"

    fx_rate = st.number_input("FX Rate", min_value=1.0000,  format="%.4f", step=0.0001, key=key_fx_rate)

    return fx_rate


def counter_settlement_section (currencies :  Optional[List[str]] = None, number_order : int = 1) :
    """
    Docstring for amount_n_currency_section
    
    :param number_order: Description
    :type number_order: int
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies

    key_amount = f"UBS_FX_Payment_{number_order}_settlement_amount"
    key_currency = f"UBS_FX_Payment_{number_order}_counter_currency"

    amount, currency = amount_currency_fields(currencies, number_order, key_amount, key_currency, "Settlement Amount", "Counter Currency")

    return amount, currency


def value_date_section (number_order : int = 1, format : str = "%d.%m.%Y") :
    """
    Docstring for value_date_section
    """
    key_date_t = f"UBS_FX_Payments{number_order}_t_date"
    key_date_v = f"UBS_FX_Payments{number_order}_m_date"
    
    col1, col2 = st.columns(2) 
    
    with col1 :
        t_date = date_selector("Trade Date", key=key_date_t)
    
    with col2 :
        v_date = date_selector("Maturity Date", key=key_date_v)

    t_date = str_to_date(t_date, format=format)
    v_date = str_to_date(v_date, format=format)

    return t_date, v_date


def bic_code_section (number_order : int = 1) :
    """
    Docstring for bic_code_section
    """
    key_bic = f"UBS_FX_Payment_{number_order}_bic"

    bic_code = st.text_input("BIC Code", key=key_bic)

    return bic_code


def export_fx_payment_section (payments : List[Tuple] = None, filename : Optional[str] = None, dir_abs_path : Optional[str] = None) :
    """
    Docstring for export_fx_payment_section
    """
    #st.write(payments)
    dataframe = create_settlement_fx_payment_excel(payments)

    st.dataframe(dataframe)
    if dataframe is None :
        
        st.warning("[-] No payment information to export")
        return None
    
    filename = f"UBS_FX_Payments_{date_to_str(date=None, format='%Y%m%d_%H%M%S')}" if filename is None else filename
    dir_abs_path = PAYMENTS_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path

    excel_filename = f"{filename}.xlsx"
    status = export_dataframe_to_excel(dataframe, output_abs_path=os.path.join(dir_abs_path, excel_filename))
    st.write(status)
    if status.get("success") is True :

        st.success(f"[+] FX Payments exported to excel successfully as {excel_filename}")

        pdf_filename = f"{filename}.pdf"
        status = export_excel_to_pdf(status.get("path"), pdf_filename, dir_abs_path, orientation=2)

        if status.get("success") is True :

            st.success(f"[+] FX Payments exported to pdf successfully as {pdf_filename}")
            st.download_button("Download PDF", data=open(status.get("path"), "rb"), file_name=pdf_filename)
        
    return None
    