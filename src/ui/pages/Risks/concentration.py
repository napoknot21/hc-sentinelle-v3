from __future__ import annotations

import datetime as dt
import streamlit as st

from typing import Optional


from src.ui.components.text import center_h2


def concentration (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("Concentration")
    return None