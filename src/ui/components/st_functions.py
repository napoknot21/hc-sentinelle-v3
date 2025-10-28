import streamlit as st
from streamlit_option_menu import option_menu


def custom_option_menu (options_list : list) :
    """
    Creates a custom option menu for a certain options

    Args :
        - options : List[disct] : list of options where each option is composed by a 'name' and 'page'
    """
    option_menu = option_menu(
        
        title=None,
        options=[option['name'] for option in options_list],
        icons=[option['icon'] for option in options_list],
        orientation="horizontal",

    )


def center (text :  str, tag :  str, additional_css_rules : str = "") :
    """
    
    """
    st.write(
    
        f"<{tag} style='text-align: center;{additional_css_rules}'>{text}</{tag}>",
        unsafe_allow_html=True
    
    )

