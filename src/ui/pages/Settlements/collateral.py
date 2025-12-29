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


def colleteral_management (default_value : int = 1) :
    """
    Docstring for colleteral_management
    """
    nb_collateral = nb_of_payments_section(default_value)

    return None


# ----------- Nb of Payement's selector -----------

def nb_of_payments_section (default_value : int = 1, max_value : int = 4) :
    """
    
    """
    nb_payments = number_of_items_selector("Select number of Cash Collateral", default_value, max_value)

    return nb_payments


