from __future__ import annotations

import streamlit as st
import datetime as dt


from src.ui.components.text import center_h2
from src.ui.components.selector import number_of_payments_selector



def process (default_value : int = 1) :
    """
    Main function that displays the Payments Process page
    """
    center_h2("Process Payments")
    nb_of_payments_section()

    return None



def nb_of_payments_section (default_value : int = 1) :
    """
    
    """
    nb_payments = number_of_payments_selector(min_value=default_value)

    return None