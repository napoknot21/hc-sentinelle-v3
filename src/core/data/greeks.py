from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt


from typing import Optional, List, Dict, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str, str_to_date
from src.utils.data_io import load_excel_to_dataframe
from src.config.parameters import FUND_HV, GREEKS_ALL_FILENAME, GREEKS_COLUMNS, GREEKS_REGEX, GREEKS_OVERVIEW_COLUMNS
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


def read_greeks_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        greeks_paths : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,
        regex : Optional[re.Pattern] = None,
        mode : str = "eq"

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    schema_overrides = GREEKS_OVERVIEW_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    regex = GREEKS_REGEX if regex is None else regex

    greeks_paths = GREEKS_FUNDS_DIR_PATHS if greeks_paths is None else greeks_paths
    dir_abs = greeks_paths.get(fund)

    filename, real_date = find_most_recent_file_by_date(date, dir_abs, regex, mode=mode) if filename is None else filename
    
    if filename is None :
        return None, None

    full_path = os.path.join(dir_abs, filename)

    try :
        dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides, specific_cols=specific_cols)

    except Exception as e :
        
        log(f"[-] Error during greeks {date_to_str(date)} file reading", "error")
        return None, None
    
    return dataframe, md5, real_date


def find_most_recent_file_by_date (
    
        date : Optional[str | dt.datetime | dt.date] = None,

        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

        mode: str = "eq",  # "eq", "le", "ge"
    
    ) -> Tuple[Optional[str], Tuple[str]] :
    """
    Return
    """
    date_str_target = date_to_str(date)

    if not os.path.isdir(dir_abs_path) :
        return None, None
    
    # Best pour la date cible
    best_per_date: Dict[str, Tuple[int, int, float, str]] = {}

    with os.scandir(dir_abs_path) as it : # 
        
        for entry in it :

            if not entry.is_file() :
                continue
            
            m = regex.match(entry.name)

            if not m :
                continue

            date_str, hh, mm = m.groups()

            hh_i = int(hh)
            mm_i = int(mm)

            mtime = entry.stat().st_mtime

            key = (hh_i, mm_i, mtime)

            current = best_per_date.get(date_str)

            if current is None or key > current[:3] :
                best_per_date[date_str] = (hh_i, mm_i, mtime, entry.name)
    
    if not best_per_date:
        return None, None
    
    # Si on a exactement la date cible, on la privilégie pour tous les modes
    if date_str_target in best_per_date:
        _, _, _, fname = best_per_date[date_str_target]
        return fname, date_str_target

    # Pas de fichier pour la date exacte -> on applique le "mode"
    all_dates = sorted(best_per_date.keys())  # tri lexical = tri chronologique

    if mode == "eq":
        # strict : rien trouvé à la date exacte
        return None, None

    elif mode == "le":
        # Dernière date <= date cible
        candidates = [d for d in all_dates if d <= date_str_target]
        if not candidates:
            return None, None
        chosen_date = candidates[-1]

    elif mode == "ge":
        # Première date >= date cible
        candidates = [d for d in all_dates if d >= date_str_target]
        if not candidates:
            return None, None
        chosen_date = candidates[0]

    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'eq', 'le' or 'ge'.")

    _, _, _, fname = best_per_date[chosen_date]
    return fname, chosen_date


