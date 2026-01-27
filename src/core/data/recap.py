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

        light : bool = True,

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
    schema_overrides = pick_columns_view(light)

    regex = TRADE_RECAP_RAW_FILE_REGEX if regex is None else regex
    filename, real_date = find_most_recent_file_by_date(date, dir_abs_path, regex, format, mode) if filename is None else (filename, None)

    if filename is None :
        
        log("[-] No files for the selected date...", "error")
        return None, None, None
    
    dir_abs_path = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path
    full_path = os.path.join(dir_abs_path, filename)

    dataframe, md5 = load_excel_to_dataframe(
        full_path,
        schema_overrides=schema_overrides
    )

    if dataframe is None :

        log ("[-] Error reading the Trade Recap dataframe", "error")
        return None, None, None
    
    if schema_overrides is not None :

        try :
            dataframe = dataframe.select(list(schema_overrides.keys()))

        except :
            
            expected_cols = list(schema_overrides.keys())
            existing_cols = set(dataframe.columns)

            missing_cols = [
            
                pl.lit(None).cast(dtype).alias(col)
                for col, dtype in schema_overrides.items() if col not in existing_cols
            
            ]

            if missing_cols :
                dataframe = dataframe.with_columns(missing_cols)

            dataframe = dataframe.select(expected_cols)

    return dataframe, md5, real_date


def pick_columns_view (
        
        light : bool = True,
        min_cols : Optional[Dict] = None,

    ) :
    """
    """
    min_cols = TRADE_RECAP_MIN_COLUMNS if min_cols is None else min_cols
    
    if light is True :
        return min_cols
    
    return None


def clean_structure_from_dataframe (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        drop_nested_struct: bool = True,
        return_dropped: bool = False,
        
    ) :
    """
    Docstring for clean_structure_from_dataframe
    """
    if dataframe is None or dataframe.is_empty():
        return (dataframe, []) if return_dropped else dataframe

    dropped: List[str] = []

    for col, dtype in dataframe.schema.items():
        # direct struct
        if dtype == pl.Struct:
            dropped.append(col)
            continue

        # nested struct (optional)
        if drop_nested_struct:
            # ex: List(Struct), Array(Struct)
            if isinstance(dtype, (pl.List, pl.Array)) and dtype.inner == pl.Struct:
                dropped.append(col)

    df2 = dataframe.drop(dropped) if dropped else dataframe
    return (df2, dropped) if return_dropped else df2



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
    return None


def apply_user_review_defaults(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add helper columns for review + recaps.
    """
    if "Label" not in df.columns :

        # AUTO means "use rule / infer later"
        df = df.with_columns(pl.lit("AUTO").cast(pl.Utf8).alias("RecapBucket"))
        
    return df


def apply_otc_fx_logic_to_trade (
        
        dataframe : Optional[pl.DataFrame],
        md5 : Optional[str] = None,

        columns : Optional[List] = None,
    
    ) -> Optional[pl.DataFrame] :
    """
    Docstring for apply_otc_fx_logic_to_trade
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    """
    columns = ["Label", "assetClass", "tradeLegCode", "tradeDescription"] if columns is None else columns

    if dataframe is None or dataframe.is_empty() :
        return None
    
    for col in columns :

        if col not in dataframe.columns :
            raise ValueError(f"Missing required column: {col}")

    # Select FX Trades
    ac = pl.col("assetClass").fill_null("").str.to_uppercase()

    text_col = (
        pl.concat_str(
            [pl.col("tradeLegCode").fill_null(""), pl.col("tradeDescription").fill_null("")],
            separator=" "
        )
        .str.to_uppercase()
    )

    is_otc = (
        ((ac == "FX") & ~text_col.str.contains(r"\b(SPOT|FORWARD|FX SWAP)\b"))
        | ((ac == "EQ") & ~text_col.str.contains(r"\bLISTED\b"))
    )


    df_fx = dataframe.with_columns(

        pl.when(is_otc)
          .then(pl.lit("OTC"))
          .otherwise(pl.lit("FX"))
          .alias("Label")
    )

    return df_fx