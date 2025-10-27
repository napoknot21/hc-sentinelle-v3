from __future__ import annotations

import polars as pl
import datetime as dt

from typing import List, Dict, Optional, Tuple, Any

from src.core.api.client import get_ice_calculator, get_trade_manager
from src.config.parameters import *
from src.utils.formatters import date_to_str


def get_cash (
        
        fund : Optional[str] = None,
        date : Optional[str] = None,

        books : Optional[List[str]] = None,

        tm : Optional[Any] = None,
        ic : Optional[Any] = None,

    ) -> Optional[pl.DataFrame] :
    """
    
    """
    fund = FUND_NAME_MAP if fund is None else fund
    date = date_to_str(date) if date is None else date


    ic = get_ice_calculator() if tm is None else tm
    tm = get_trade_manager() if ic is None else ic



def fetch_subread_data (
        
        fund : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        rename_cols = None,
        select_cols = None,
        books : Optional[List[str]] = None,
    
    ) :
    """
    
    """
    fund = None
    date = date_to_str(date)
    books = ["WR_VAULT"] if books is (None or (None)) else None 
    trade_manager = get_trade_manager()
    calculator = get_ice_calculator()



