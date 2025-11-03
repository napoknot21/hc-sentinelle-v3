import threading
import streamlit as st

from pathlib import Path

from src.ui.components.layout import header, sidebar
from src.ui.styles.base import risk_menu

from src.ui.pages.Payments.render import render_payments
from src.ui.pages.Risks.render import render_risks


PAGES = [

    ("Risks",           "exclamation-triangle-fill",    render_risks),
    #("Reconciliation", "arrow-repeat",                 render_reco),
    #("Ice API",        "server",                       render_trading),
    ("Payments",        "cash",                         render_payments),
    #("Statistics",     "graph-up",                     render_stats),

]


def app () :

    st.set_page_config(layout="wide")

    logo = Path(__file__).parent / "assets" / "logos" / "heroics-logo-bleu.png"
    header(title=None, subtitle=None, logo_path=logo) #,  subtitle=None, logo_width=300, center=True)

    selected = sidebar(PAGES, "Heroics Capital", logo_header_path=str(logo), styles=risk_menu)
    
    for name, _icon, render in PAGES :

        if selected == name :

            render()
            break
    