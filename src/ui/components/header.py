import os
import streamlit as st

from pathlib import Path
from typing import Optional

@st.cache_data()
def render_header (
        
        logo_path: str | Path,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        logo_width: int = 300,
        center: bool = True,
    
    ) -> None :
    """
    Render the top header with a logo and optional title/subtitle.
    Must be called AFTER st.set_page_config() in app.py.
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
            st.image(str(p), width=logo_width)
        
        if title :
            st.markdown(f"## {title}")
        
        if subtitle :
            st.caption(subtitle)

    return None
