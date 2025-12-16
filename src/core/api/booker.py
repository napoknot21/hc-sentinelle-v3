from __future__ import annotations

import os
import sys
import datetime as dt

from typing import Optional

from src.config.paths import LIBAPI_ABS_PATH
sys.path.append(LIBAPI_ABS_PATH)

from src.utils.formatters import date_to_str
from src.utils.logger import log
from libapi.ice.trade_manager import TradeManager # type: ignore


def post_margin_call_on_ice (
        
        amount : float | int,
        currency : str,
        counterparty : str,
        direction : str,
        date : Optional[str | dt.datetime | dt.date] = None,
        book : Optional[str] = None,

        loopback : int = 5
    
    ) :
    """
    Docstring for post_margin_call_on_ice
    """
    if loopback < 0 :

        log("[-] Error during Call API", "error")
        return None

    date = date_to_str(date)
    tm = TradeManager()

    response = tm.post_margin_call(currency, date, amount, book, counterparty, direction)

    if response is None :

        log("[*] Retrying API Call", "warning")
        return post_margin_call_on_ice(
            currency, date, amount, book, counterparty, direction, loopback-1
        )

    return response