from __future__ import annotations

import hashlib

import polars as pl
import datetime as dt

from typing import Optional, Dict, List

from src.config.parameters import FUND_HV, FUND_NAME_MAP, SIMM_RENAME_COLUMNS, SIMM_COLUMNS
from src.utils.formatters import date_to_str, str_to_date
from src.utils.logger import log

from src.core.api.client import get_ice_calculator


def fetch_raw_simm_data_by_date (
    
        date : Optional[str | dt.datetime | dt.date] = None,

        fund : Optional[str] = None,
        fund_map : Optional[Dict] = None
    
    ) -> Optional[List[Dict]] :
    """
    Fetch raw bilateral SIMM (ICE) and return (df, md5) or None.

    Args :
        date (str | datetime | date): The date for which to retrieve SIMM data.
        fund (str): Fund identifier used in the API call.

    Returns:
        normal_json (pl.DataFrame | None) : A normalized Polars DataFrame containing the SIMM data, or None if the API call or normalization fails.
        md5 (str | None) : MD5 hash for the normal_json content, in order to get a local cache

    Note :
        This function refers to the "get_simm()" precedent version.
    """
    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund

    fund_map = FUND_NAME_MAP if fund_map is None else fund_map
    fund_name = fund_map.get(fund, "HV")

    if not fund_name :

        log(f"[-] Fund '{fund}' not found in FUND_NAME_MAP", "error")
        return None
    
    # Ice API connexion
    try :

        ic = get_ice_calculator()
        log(f"[+] ICE API client ready | fund : {fund_name} | date : {date}", "info")

    except Exception as e :

        log(f"[-] ICE API initialization failed: {e}", "error")
        return None
    
    # Network bound
    try :

        bilateral_im = ic.get_bilateral_im_calculation_all_ctpy(date, fund_name)
        
        if bilateral_im is None :
        
            log(f"[-] Error during bilateral IM data request | fund={fund_name} | date={date}", "error")
            return None

    except Exception as e :

        log(f"[-] Error during bilateral IM request: {e}", "error")
        return None

    log("[+] Bilateral IM data request successful")
    
    return bilateral_im


def convert_raw_simm_to_dataframe (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        raw_simm : Optional[List[Dict]] = None,

        rename_columns : Optional[Dict] = None,
        simm_columns : Optional[Dict] = None

    ) :
    """
    """
    date = str_to_date(date)

    rename_columns = SIMM_RENAME_COLUMNS if rename_columns is None else rename_columns
    simm_columns = SIMM_COLUMNS if simm_columns is None else simm_columns

    if raw_simm is None or len(raw_simm) <= 0 :
        return None, None
    
    dataframe = pl.DataFrame(raw_simm)

    col_meta = {k: (v["name"], v["type"]) for k, v in simm_columns.items()}

    flat_cols   = {}  # { raw_col: (final_name, dtype) }
    struct_cols = {}  # { struct_col: { field: (final_name, dtype) } }

    for raw_key, (final_name, dtype) in col_meta.items() :

        if "." in raw_key :

            struct_col, field = raw_key.split(".", 1)
            struct_cols.setdefault(struct_col, {})[field] = (final_name, dtype)
        
        else :
            flat_cols[raw_key] = (final_name, dtype)

    exprs = [

        *[
            pl.col(struct_col).struct.field(field).cast(dtype).alias(final_name)
            for struct_col, fields in struct_cols.items()
            if struct_col in (columns := pl.DataFrame(raw_simm).columns)
            for field, (final_name, dtype) in fields.items()
        ],
        
        *[
            pl.col(raw_col).cast(dtype).alias(final_name)
            for raw_col, (final_name, dtype) in flat_cols.items()
        ],
    
    ]

    final_cols = [final_name for _, (final_name, _) in col_meta.items()] + ["Date"]

    dataframe = (
        pl.DataFrame(raw_simm)
        .with_columns(exprs)
        .with_columns(pl.lit(date).alias("Date").cast(pl.Date))
        .select(final_cols)
    )

    md5 = hashlib.md5(dataframe.write_csv().encode()).hexdigest()

    return dataframe, md5

