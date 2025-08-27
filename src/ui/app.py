import streamlit as st

from pathlib import Path

from src.ui.components.header import *
from src.ui.pages.Payments.payments import show_payments_page


def render_app () :
    # ❌ NE PAS appeler st.set_page_config ici

    # Imports Streamlit tiers et pages APRES la config (pour éviter tout st.* top-level)
    from streamlit_option_menu import option_menu
    from src.ui.pages.Payments.payments import show_payments_page

    css = Path(__file__).parent / "styles" / "base.css"
    if css.exists():
        st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

    logo = Path(__file__).parent / "assets" / "logos" / "heroics-logo-bleu.png"
    if logo.exists():
        st.image(str(logo), width=300)

    PAGES = [("Payment Machine", "cash", show_payments_page)]
    names = [p[0] for p in PAGES]
    icons = [p[1] for p in PAGES]

    with st.sidebar:
        st.markdown("# Heroics Capital")
        selected = option_menu(None, names, icons=icons, default_index=0)
        st.link_button("Access Heroics Aegis", "http://192.168.124.27:9999/")

    for name, _icon, render in PAGES:
        if selected == name:
            render()
            break