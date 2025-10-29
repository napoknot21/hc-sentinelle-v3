from __future__ import annotations

from streamlit_option_menu import option_menu


from src.ui.pages.Payments.booker import *
from src.ui.pages.Payments.display import *
from src.ui.pages.Payments.payments import *

from src.ui.components.text import center_h1, center_h3
from src.ui.styles.base import risk_menu

payments_subpages = [

    {"name" : "Process",},
    {"name" : "Security",},
    {"name" : "Display"},
    {"name" : "Booker"}

]


def render_payments_page (title : str = "Payments", subtitle : str = "Back Office Tool", fundation_map : Optional[Dict] = None) :
    """
    
    """

    # title here
    center_h1(title)
    center_h3(subtitle)

    menu = option_menu(

        menu_title=None,
        options=[subpage["name"] for subpage in payments_subpages],
        #icons=[subpage["icon"] for subpage in payments_subpages],
        orientation="horizontal",
        default_index=0, 
        styles=risk_menu

    )
