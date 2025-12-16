from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.config.parameters import PAYMENTS_CONCURRENCIES, PAYMENTS_COUNTERPARTIES, PAYMENTS_DIRECTIONS, PAYMENTS_BOOKS

from src.ui.components.selector import date_selector
from src.ui.components.input import amount_currency_fields
from src.ui.components.text import center_h2

from src.core.api.booker import post_margin_call_on_ice

def booker () :
    """
    
    """
    center_h2("Booker")

    amount, currency = amount_currency_section()
    ctpy, direction = counterparty_n_direction_section()
    date = date_selector("Value Date")
    book = book_section()

    if st.button("Post Margin Call") :

        post_margin_call(amount, currency, ctpy, direction, date, book)

    return None


def amount_currency_section (currencies : Optional[List[str]] =  None) :
    """
    Docstring for amount_currency_section
    
    :param currencies: Description
    :type currencies: Optional[List[str]]
    """
    currencies = PAYMENTS_CONCURRENCIES if currencies is None else currencies
    amount, currency = amount_currency_fields(currencies)

    return amount, currency


def counterparty_n_direction_section (
        
        counterparties : Optional[Dict] = None,
        directions : Optional[List[str]] = None,

    ) -> Tuple[Optional[str], Optional[str]] :
    """
    Docstring for counterparty_n_direction_section
    
    :param counterparties: Description
    :type counterparties: Optional[Dict]
    :param directions: Description
    :type directions: Optional[List[str]]
    :return: Description
    :rtype: Tuple[str | None, str | None]
    """
    counterparties_dict = PAYMENTS_COUNTERPARTIES if counterparties is None else counterparties
    counterparties = list(counterparties_dict.keys())

    directions = PAYMENTS_DIRECTIONS if directions is None else directions

    counterparty = st.selectbox("Counterparty", options=counterparties, key=f"payments_booker_ctpy")
    direction = st.selectbox("Direction", options=directions, key=f"payments_booker_direction")

    return counterparty, direction


def book_section (books : Optional[List[str]] = None) :
    """
    
    """
    books = PAYMENTS_BOOKS if books is None else books
    book = st.selectbox("Book", options=books)

    return book


def post_margin_call (
        
        amount : float | int,
        currency : str,
        counterparty : str,
        direction : str,
        date : Optional[str | dt.datetime | dt.date] = None,
        book : Optional[str] = None,     

    ) :
    """
    Docstring for post_margin_call
    """
    response = post_margin_call_on_ice(amount, currency, counterparty, direction, date, book)
    #st.write(response)
    if response is None :

        st.error("LibAPI Error. Check your libApi")
        return None
    
    if response.get("status") == "Success" :
        st.success("Margin Call Succesfully posted on ICE")

    else :
        st.warning("Error During Post Margin call. Try later or again.")
    
    return None