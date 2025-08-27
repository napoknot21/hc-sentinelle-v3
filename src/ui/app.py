import threading
import streamlit as st

from pathlib import Path

from src.ui.components.header import render_header
from src.ui.components.sidebar import render_sidebar

from src.ui.pages.Payments.payments import render_payments


PAGES = [
    #("Risks", "exclamation-triangle-fill", render_risks),
    #("Reconciliation", "arrow-repeat", render_reco),
    #("Ice API (but better)", "server", render_trading),
    ("Payment Machine", "cash", render_payments),
    #("Statistics", "graph-up", render_stats),
]


def render_app () :

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