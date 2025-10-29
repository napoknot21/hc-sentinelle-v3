from __future__ import annotations

import polars as pl
import pandas as pd
import datetime as dt

import streamlit as st
from streamlit_option_menu import option_menu

from typing import Dict, Optional

from src.utils.formatters import date_to_str
from src.config.parameters import FUND_NAME_MAP

from src.ui.pages.Risks.expiries import expiries
from src.ui.pages.Risks.performance import *
from src.ui.pages.Risks.fx_screeners import *
from src.ui.pages.Risks.greeks import *
from src.ui.pages.Risks.portfolio import *
from src.ui.pages.Risks.cash import *

from src.ui.styles.base import risk_menu
from src.ui.components.selector import date_selector
from src.ui.components.text import center_h1

risk_subpages = [
    
    {"name" : "Expiries",       "page" : expiries,  "icon" : "calendar-check"},
    {"name" : "Cash",           "page" : cash,      "icon" : "cash-stack"},

]



def render_risk_page (title : str = "Risks", fundation_map : Optional[Dict] = None) -> None :
    """
    
    """
    fundation_map = FUND_NAME_MAP if fundation_map is None else fundation_map
    fund_options = list(fundation_map.keys())

    # Title here
    center_h1(title)

    date_col, fund_col = st.columns(2)

    
    with date_col :
        
        date = date_selector(label="Select a date ")
        st.cache_data.clear()

    fundation = fund_col.selectbox("Select a fund ", fund_options)

    st.cache_data.clear()

    menu = option_menu(

        menu_title=None,
        options=[subpage["name"] for subpage in risk_subpages],
        icons=[subpage["icon"] for subpage in risk_subpages],
        orientation="horizontal",
        default_index=0, 
        styles=risk_menu

    )


    for subpage in risk_subpages :

        if subpage["name"] == menu and not subpage["page"] is None :
            subpage["page"](date, fundation)







