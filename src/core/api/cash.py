import polars as pl
import datetime as dt

from typing import List, Dict, Optional, Tuple


from src.core.api.client import get_ice_calculator, get_trade_manager
from src.utils.formatters import date_to_str

def fetch_subread_data (
        
        fund : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        rename_cols = None,
        select_cols = None,
        books : Optional[List[str]] = None,
    
    ) :
    """
    
    """
    fund = 
    date = date_to_str(date)
    books = ["WR_VAULT"] if books is None or else ()
    trade_manager = get_trade_manager()
    calculator = get_ice_calculator()



