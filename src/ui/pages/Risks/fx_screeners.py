from __future__ import annotations

import os
import polars as pl
import datetime as dt

from typing import Optional

from src.ui.components.text import center_h1, center_h2


def fx_screeners (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("FX Screeners")

    tarf_section(date, fundation)
    fx_carry_section(date, fundation)

    return None


def tarf_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None

    ) :
    """
    
    """

    return None


def fx_carry_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None

    ) :
    """

    """
    return None

