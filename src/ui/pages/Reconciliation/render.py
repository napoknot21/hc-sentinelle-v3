from __future__ import annotations

import streamlit as st
import datetime as dt

from streamlit_option_menu import option_menu

from src.ui.components.text import center_h1
from src.ui.styles.base import risk_menu

from src.ui.pages.Reconciliation.general import general
from src.ui.pages.Reconciliation.counterparty import counterparty

reconciliation_subpages = [
    
    {"name" : "General",            "page" : general,       "icon" : "calendar-check"},
    {"name" : "Per Counterparty",   "page" : counterparty,  "icon" : "cash-coin"},
    
]


def render_reconciliation (title : str = "Reconciliation Page") :
    """
    
    """
    center_h1(title)
    st.write('')

    menu = option_menu(

        menu_title=None,
        options=[subpage["name"] for subpage in reconciliation_subpages],
        icons=[subpage["icon"] for subpage in reconciliation_subpages],
        orientation="horizontal",
        default_index=0, 
        styles=risk_menu

    )

    for subpage in reconciliation_subpages :

        if subpage["name"] == menu and not subpage["page"] is None :
            subpage["page"]()
    
    return None