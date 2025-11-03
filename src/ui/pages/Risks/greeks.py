from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import Optional

from src.ui.components.text import center_h2

def greeks (

        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("Greeks")

    return None