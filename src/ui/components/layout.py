from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional

import streamlit as st
from streamlit_option_menu import option_menu
from src.ui.components.text import center_h2


def header (
        
        title : Optional[str] = None,
        subtitle : Optional[str] = None,
        logo_path : Optional[str | Path] = None,
        logo_width : int = 300,
        center : bool = True
    
    ) :
    """
    
    """
    p = Path(logo_path)

    if center :

        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
        
            if p.exists():
                st.image(str(p), width=logo_width)
        
            if title:
                st.markdown(
                    f"<h1 style='text-align:center;margin:0'>{title}</h1>",
                    unsafe_allow_html=True,
                )

            if subtitle:
                st.markdown(
                    f"<div style='text-align:center;opacity:.75'>{subtitle}</div>",
                    unsafe_allow_html=True,
                )
    else :

        if p.exists() :
            st.image(str(p))#, width="stretch")
        
        if title :
            st.markdown(f"## {title}")
        
        if subtitle :
            st.caption(subtitle)

    return None


def sidebar (groupes : List[Dict[str, str]], title : str = "", logo_header_path : Optional[str] = None, styles : Optional[Dict] = None) :
    """
    From a group of tabs, it will create a graphical sidebar
    """
    names = [p[0] for p in groupes]
    icons = [p[1] for p in groupes]

    sidebar = st.sidebar

    with sidebar:

        if logo_header_path:
            st.image(logo_header_path)#, width='stretch')

        center_h2(title)
        
        selected = option_menu(
            None,
            names,
            icons=icons,
            styles=styles
        )
        st.cache_data.clear()

        footer_aegis("http://localhost:9999")

    # update query params for deep linking
    st.query_params["page"] = selected
    
    return selected


def footer_aegis (link : Optional[str] = None) :
    """
    
    """
    if link :

        aegis = st.link_button("Access Heroics Aegis", link)

    return aegis

    


