from __future__ import annotations

import os
import re
import json
import polars as pl
import datetime as dt

from typing import Optional, Dict, List

from src.utils.formatters import date_to_str

from src.config.parameters import SUBRED_FILENAME_REGEX
from src.config.paths import SUBRED_AUM_CACHE_ABS_PATH

def read_aum_from_cache (
        
        date : Optional[str | dt.datetime | dt.date] = None, 
        filename : Optional[str] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

    ) :
    """
    
    """
    date = date_to_str(date)
    regex = SUBRED_FILENAME_REGEX if regex is None else regex

    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path
    filename = find_cache_file_by_date(date, regex=regex) if filename is None else filename

    if filename is None :
        return None
    
    full_path = os.path.join(dir_abs_path, filename)

    with open(full_path, "r+", encoding="utf-8") as f :
        data = json.load(f)

    return data


def find_cache_file_by_date (

        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,    

    ) -> Optional[str] :
    """
    
    """
    date = date_to_str(date)
    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path
    regex = SUBRED_FILENAME_REGEX if regex is None else regex

    os.makedirs(dir_abs_path, exist_ok=True)

    with os.scandir(dir_abs_path) as it : 
        
        for entry in it :

            if not entry.is_file() :
                continue

            m = regex.match(entry.name)

            if not m :
                continue
            
            date_str = m.groups()

            if date_str[0] == date :
                return entry.name

    return None


def save_aum_to_cache (
        
        aum_dict : Dict,
        date : Optional[str | dt.datetime | dt.date] = None,
        dir_abs_path : Optional[str] = None
        
    ) -> bool :
    """
    
    """
    date = date_to_str(date)
    dir_abs_path = SUBRED_AUM_CACHE_ABS_PATH if dir_abs_path is None else dir_abs_path

    os.makedirs(dir_abs_path, exist_ok=True)

    if aum_dict is None :

        print("\n[-] Nothing was saved. Continuing...")
        return False
    
    filename = f"{date}_aum.json"
    full_path = os.path.join(dir_abs_path, filename)

    try :

        # Write JSON file
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(aum_dict, f, indent=4)

    except Exception as e :
     
        return False
    
    return True
    

    
