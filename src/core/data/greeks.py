from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt


from typing import Optional, List, Dict, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str, str_to_date
from src.utils.data_io import load_excel_to_dataframe
from src.config.parameters import FUND_HV, GREEKS_ALL_FILENAME, GREEKS_COLUMNS
from src.config.paths import GREEKS_FUNDS_DIR_PATHS


def read_history_greeks (

        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        greeks_paths : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    schema_overrides = GREEKS_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    greeks_paths = GREEKS_FUNDS_DIR_PATHS if greeks_paths is None else greeks_paths
    filename = GREEKS_ALL_FILENAME if filename is None else filename

    dir_abs = greeks_paths.get(fund)
    full_path = os.path.join(dir_abs, filename)

    try :
        dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides, specific_cols=specific_cols)

    except Exception as e :
        
        log("[-] Error during greeks history file reading", "error")
        return None, None
    
    return dataframe, md5