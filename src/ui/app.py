import threading
import streamlit as st

from pathlib import Path

from src.ui.components.header import render_header
from src.ui.components.sidebar import render_sidebar

from src.ui.pages.Payments.payments import render_payments
from src.ui.pages.Payments.render import render_payments_page
from src.ui.pages.Risks.render import render_risk_page

PAGES = [
    ("Risks", "exclamation-triangle-fill", render_risk_page),
    #("Reconciliation", "arrow-repeat", render_reco),
    #("Ice API (but better)", "server", render_trading),
    ("Payments", "cash", render_payments_page),
    #("Statistics", "graph-up", render_stats),
]


def app () :

    st.set_page_config(layout="wide")

    logo = Path(__file__).parent / "assets" / "logos" / "heroics-logo-bleu.png"
    render_header(logo, title=None, subtitle=None, logo_width=300, center=True)

    params = st.query_params
    names = [p[0] for p in PAGES]

    default_index = (names.index(params["page"]) if "page" in params and params["page"] in names else 0)

    selected = render_sidebar("Heroics Capital", PAGES, default_index, aegis_url="http://localhost:9999/", show_logo=False, logo_path=str(logo))

    
    for name, _icon, render in PAGES :

        if selected == name :

            render()
            break
    