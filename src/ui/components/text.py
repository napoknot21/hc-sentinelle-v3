from __future__ import annotations

import streamlit as st

from src.ui.styles.base import bold_text


# -------------- Center --------------


def center_h1 (text : str) :
    """
    
    """
    center(text, "h1")


def center_h2 (text : str) :
    """
    
    """
    center(text, "h2")


def center_h3 (text : str) :
    """
    
    """
    center(text, "h3")


def center_paragraph (text : str) :
    """
    
    """
    center(text, "p")


def center_bold_paragraph (text : str) :
    """
    
    """
    center(text, "p", bold_text)


# -------------- Left --------------


def left_h1 (text : str) :
    """
    
    """
    left(text, "h1")


def left_h2 (text : str) :
    """
    
    """
    left(text, "h2")


def left_h3 (text : str) :
    """
    
    """
    left(text, "h3")



# --------- General Functions --------- 


def center (text : str, tag : str, extra_css : str = "") :
    """
    
    """
    st.write(

        f"<{tag} style='text-align : center;{extra_css}'>{text}</{tag}>",
        unsafe_allow_html=True

    )


def left (text : str, tag : str, extra_css : str = "") :
    """
    
    """
    st.write(

        f"<{tag} style='text-align: left;{extra_css}'>{text}</{tag}>",
        unsafe_allow_html=True   

    )


def right (text : str, tag : str, extra_css : str = "") :
    """
    
    """
    st.write(

        f"<{tag} style='text-align: right;{extra_css}'>{text}</{tag}>",
        unsafe_allow_html=True   
        
    )


