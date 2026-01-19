from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt

from typing import List, Optional, Dict, Tuple

from src.config.paths import TREADE_RECAP_DATA_RAW_DIR_ABS_PATH
from src.config.parameters import TRADE_RECAP_RAW_FILE_REGEX, TRADE_RECAP_MIN_COLUMNS

from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import str_to_date, date_to_str
from src.utils.logger import log




def read_trade_recap_by_date (

        date : Optional[str | dt.datetime | dt.date] = None,

        filename : Optional[str] = None,
        dir_abs_path : Optional[str] = None,

        schema_overrides : Optional[Dict] = None,
        regex : Optional[re.Pattern] = None,
        
        format : str = "%Y_%m_%d",
        mode : str = "le",

    ) : 
    """
    Docstring for read_trade_recap_by_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param filename: Description
    :type filename: Optional[str]
    :param schema_overrides: Description
    :type schema_overrides: Optional[Dict]
    :param regex: Description
    :type regex: Optional[re.Pattern]
    :param mode: Description
    :type mode: str
    """
    date = str_to_date(date) 
    
    schema_overrides = TRADE_RECAP_MIN_COLUMNS if schema_overrides is None else schema_overrides
    #columns = list(schema_overrides.keys())

    regex = TRADE_RECAP_RAW_FILE_REGEX if regex is None else regex
    filename, real_date = find_most_recent_file_by_date(date, dir_abs_path, regex, format, mode) if filename is None else (filename, None)

    if filename is None :
        
        log("[-] No files for the selected date...", "error")
        return None, None, None
    
    dir_abs_path = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path
    full_path = os.path.join(dir_abs_path, filename)

    dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides)

    if dataframe is None :

        log ("[-] Error reading the Trade Recap dataframe", "error")
        return None, None, None
    
    return dataframe, md5, real_date



def pick_default_columns (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        columns : Optional[Dict] = None,
        default_cols : Optional[int] = 12,

    ) -> List[str] :
    """
    Adjust the priority list to your trade recap schema.
    Falls back to first non-null-ish columns if nothing matches.
    """
    columns = TRADE_RECAP_MIN_COLUMNS if columns is None else columns

    priority = list(columns.keys())
    cols = [c for c in priority if c in dataframe.columns]

    # fallback: first 12 columns
    if not cols :
        cols = dataframe.columns[:default_cols]

    # avoid too many by default
    return cols[:15]




def find_most_recent_file_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,

        dir_abs_path : Optional[str] = None,
        regex : Optional[str] = None,

        format : str = "%Y_%m_%d",
        mode: str = "le",  # "eq", "le", "ge"

    ) -> Tuple[Optional[str], Tuple[str]] :
    """
    Docstring for find_most_recent_file_by_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param dir_abs_path: Description
    :type dir_abs_path: Optional[str]
    :param regex: Description
    :type regex: Optional[str]
    """
    date_str_target = date_to_str(date)

    dir_abs_path = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path
    regex = TRADE_RECAP_RAW_FILE_REGEX if regex is None else regex

    if not os.path.isdir(dir_abs_path) :
        return None, None
    
    # Best pour la date cible
    best_per_date: Dict[str, Tuple[int, int, float, str]] = {}

    with os.scandir(dir_abs_path) as it :
        
        for entry in it :

            if not entry.is_file() :
                continue
            
            m = regex.match(entry.name)

            print(entry.name)
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
    date_str_target = str_to_date(date_str_target) 

    if mode == "eq":
        # strict : rien trouvé à la date exacte
        return None, None

    elif mode == "le" :
        # last date <= date target
        candidates = [d for d in all_dates if str_to_date(d, format) <= date_str_target]

        if not candidates :
            return None, None

        chosen_date = candidates[-1]

    elif mode == "ge" :
        # First date >= date Target
        candidates = [d for d in all_dates if str_to_date(d, format) >= date_str_target]

        if not candidates :
            return None, None
        
        chosen_date = candidates[0]

    else :
        
        log(f"Unknown mode '{mode}'. Use 'eq', 'le' or 'ge'.")
        return None, None
    
    _, _, _, fname = best_per_date[chosen_date]
    
    return fname, chosen_date



def build_master_trade_recap_draft (
        
        date : Optional[str | dt.datetime | dt.date] = None,

        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

    ) :
    """
    Docstring for build_master_trade_recap_draft
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    """