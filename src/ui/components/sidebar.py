# src/ui/components/sidebar.py
from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu

from typing import Callable, Sequence

PageEntry = tuple[str, str, Callable[[], None]]  # (name, icon, render_fn)

def render_sidebar (
    
        app_title: str,
        pages: Sequence[PageEntry],
        default_index: int = 0,
        aegis_url: str | None = None,
        show_logo: bool = False,
        logo_path: str | None = None,
    
    ) -> str:
    """
    Render the sidebar with navigation and return the selected page name.
    - `pages`: list of tuples (name, icon, render_function)
    - `aegis_url`: optional external link button
    """
    names = [p[0] for p in pages]
    icons = [p[1] for p in pages]

    sidebar = st.sidebar

    with sidebar:

        if show_logo and logo_path:
            st.image(logo_path, width='stretch')

        st.markdown("### " + app_title)

        selected = option_menu(
            None,
            names,
            icons=icons,
            default_index=default_index,
            styles={
                "container": {
                    "background-color": st.get_option("theme.secondaryBackgroundColor")
                },
                "nav-link": {"margin": "0", "padding": "6px 8px", "font-size": "12px"},
                "nav-link-selected": {"background-color": "#7645FF", "color": "white"},
            },
        )
        st.cache_data.clear()

        if aegis_url:
            st.link_button("Access Heroics Aegis", aegis_url)

    # update query params for deep linking
    st.query_params["page"] = selected
    
    return selected