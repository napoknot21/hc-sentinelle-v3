from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu
from typing import Optional, Dict

from src.ui.pages.Payments.booker import *
from src.ui.pages.Settlements.payments import payments_process
from src.ui.pages.Settlements.collateral import colleteral_management
from src.ui.pages.Settlements.booker import booker
from src.ui.pages.Payments.process import process

from src.ui.components.text import center_h1, center_h3
from src.ui.styles.base import risk_menu

payments_subpages = [

    {"name" : "Process Payment UBS",    "page": payments_process,   "icon": "cash-coin"},
    {"name" : "Collateral Management", "page" : colleteral_management, "icon" : "cash-coin"},
    #{"name" : "Display",    "page" : display,   "icon" : "eye"},
    {"name" : "Booker",     "page" : booker,    "icon" : "book"},

]


def render_ (title : str = "Payments", subtitle : str = "Back Office Tool", fundation_map : Optional[Dict] = None) :
    """
    
    """

    # title here
    center_h1(title)
    center_h3(subtitle)
    st.write('')

    menu = option_menu(

        menu_title=None,
        options=[subpage["name"] for subpage in payments_subpages],
        icons=[subpage["icon"] for subpage in payments_subpages],
        orientation="horizontal",
        default_index=0, 
        styles=risk_menu

    )

    for subpage in payments_subpages :

        if subpage["name"] == menu and not subpage["page"] is None :
            subpage["page"]()
