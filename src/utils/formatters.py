from __future__ import annotations

import os
import re
import time
import hashlib
import calendar

import pandas as pd
import polars as pl
import datetime as dt

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from src.utils.logger import log


def date_to_str (date : Optional[str | dt.date | dt.datetime] = None, format : str = "%Y-%m-%d") -> str :
    """
    Convert a date or datetime object to a string in "YYYY-MM-DD" format.

    Args:
        date (str | datetime): The input date.

    Returns:
        str: Date string in "YYYY-MM-DD" format.
    """
    if date is None:
        date_obj = dt.datetime.now()

    elif isinstance(date, dt.datetime):
        date_obj = date

    elif isinstance(date, dt.date):  # handles plain date (without time)
        date_obj = dt.datetime.combine(date, dt.time.min) # This will add 00 for the time

    elif isinstance(date, str) :

        try:
            date_obj = dt.datetime.strptime(date, format)

        except ValueError :
            
            try :
                date_obj = dt.datetime.fromisoformat(date)
            
            except ValueError :
                raise ValueError(f"Unrecognized date format: '{date}'")
    
    else :
        raise TypeError("date must be a string, datetime, or None")

    return date_obj.strftime(format)


def str_to_date (date : Optional[str | dt.date | dt.datetime] = None, format : str = "%Y-%m-%d") -> dt.date :
    """
    
    """
    if date is None :
        date_obj = dt.date.today()
    
    if isinstance (date, dt.datetime):
        date_obj = date.date()

    if isinstance(date, dt.date) :
        date_obj = date
    
    if isinstance(date, str) :
        date_obj = dt.datetime.strptime(date, format).date()
    
    return date_obj


def shift_months (date : Optional[str | dt.date | dt.datetime] = None, months : int = 1) -> dt.date :
    """
    
    """
    date_obj = str_to_date(date)

    y0, m0 = date_obj.year, date_obj.month
    
    i = (m0 - 1) + months
    y = y0 + i // 12
    m = (i % 12) + 1
    
    last = calendar.monthrange(y, m)[1]

    return dt.date(y, m, min(date_obj.day, last))


def monday_of_week (date : Optional[str | dt.date | dt.datetime] = None) -> dt.date :
    """
    
    """
    date_obj = str_to_date(date)
    monday = date_obj - dt.timedelta(days=date_obj.weekday())
    
    return monday  # Monday..Sunday = 0..6


def check_email_format (email : str) -> bool :
    """
    Validates the format of an email address using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email matches the expected format, False otherwise.

    Note:
        This validation checks for a general pattern like 'user@domain.tld' 
        but does not guarantee that the email address actually exists.
    """
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

    return re.match(email_regex, email) is not None


def dataframe_fingerprint (dataframe : pl.DataFrame) -> str:
    """
    Deterministic & fast fingerprint based on 64-bit row hashes.
    Uses native polars hashing (no string casting, no CSV roundtrip).
    """
    # One pass hash over all columns; stable across a given Polars version.
    # For stronger digest but still fast, md5 the u64 bytes.
    h = dataframe.hash_rows(seed=0).to_numpy()  # u64 array
    
    return hashlib.md5(h.tobytes()).hexdigest()


def format_numeric_column (dataframe : pl.DataFrame, column : str, round_v : int = 2) -> pl.DataFrame :
    """
    Formats a numeric column in a DataFrame by:
    - removing commas from the values (e.g., "1,000" -> "1000")
    - converting values to float
    - rounding to 'round_v' decimal places
    - formatting as strings with thousands separators and fixed decimal places

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Name of the column to format
        round_v (int, optional): Number of decimals to round to (default=2)

    Returns:
        pd.DataFrame: A copy of the DataFrame with the formatted column as strings
    """
    df_cols = pl.col(column).cast(pl.Utf8)
    no_commas = df_cols.col.str.replace(",", "")

    as_float = no_commas.cast(pl.Float64)
    rounded = as_float.round(round_v)

    fmt_string = f"{{:,.{round_v}f}}"

    formatted = rounded.map_elements(

        lambda x: fmt_string.format(x) if x is not None else None,
        return_dtype=pl.Utf8

    )

    new_df = dataframe.with_columns([
        formatted.alias(column)
    ])

    return new_df


def get_closest_file_timestamp (file_abs_path : str , suffix : str, date : str | dt.datetime, lastest : bool = True) :
    """
    
    """
    prefix = os.path.basename(file_abs_path) # filename
    directory = os.path.dirname(file_abs_path)

    try :
        files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(suffix)]

    except FileNotFoundError :
        return None
    
    dates = []
    for f in files :

        raw = f[len(prefix) : -len(suffix)]

        try :
            dates.append(dt.strptime(raw, "%Y-%m-%d_%H-%M"))

        except ValueError :
            continue

    if not dates :
        return None
    
    if lastest :
        # Restrict to same day files
        same_day = [d for d in dates if d.date() == date.date()]

        if same_day :
            return max(same_day) # latest of the day

    return min(dates, key=lambda d: abs(d - date))


def get_most_recent_file_for_date (
        
        date : str | dt.datetime | dt.date,
        fundation : str,
        directory_map : Dict,
        regex : re.Pattern,
        extension : str = ".xlsx", 
    
    ) -> Optional[str] :
    """
    
    """
    start = time.time()

    date = date_to_str(date)
    target_day = dt.datetime.strptime(date, "%Y-%m-%d").date()

    dir_abs_path = directory_map.get(fundation)

    # Track best candidate as (timestamp, path)
    best_ts : Optional[dt.datetime] = None
    best_path : Optional[Path] = None

    root = Path(dir_abs_path)
    with os.scandir(root) as it :

        for entry in it :

            if not entry.is_file() :
                continue

            name = entry.name

            if not name.lower().endswith(extension) :
                continue

            stem = os.path.splitext(name)[0]
            m = regex.match(stem)

            if not m :
                continue

            day_str, hhmm_str = m.group(1), m.group(2)

            try :

                d = dt.datetime.strptime(day_str, "%Y-%m-%d").date()
                t = dt.datetime.strptime(hhmm_str, "%H-%M").time()

            except ValueError :

                continue

            if d != target_day :
                continue

            ts = dt.datetime.combine(d, t)

            if (best_ts is None) or ts > best_ts :

                best_ts = ts
                best_path = Path(entry.path)

    log(f"[*] Search done in {time.time() - start:.2f} seconds")
    
    return best_path


def get_most_recent_file (
    
        fundation : str,
        directory_map : Dict,
        regex : re.Pattern,
        extension : str = ".xlsx",
    
    ) -> Optional[str] :
    """
    
    """
    start = time.time()

    dir_abs_path = directory_map.get(fundation)

    root = Path(dir_abs_path)

    # Track best candidate as (timestamp, path)
    best_ts : Optional[dt.datetime] = None
    best_path : Optional[Path] = None

    with os.scandir(root) as it :

        for entry in it :

            if not entry.is_file() :
                continue

            name = entry.name

            if not name.lower().endswith(extension) :
                continue

            stem = os.path.splitext(name)[0]
            m = regex.match(stem)

            if not m :
                continue
            
            day_str, hhmm_str = m.group(1), m.group(2)

            try :

                d = dt.datetime.strptime(day_str, "%Y-%m-%d").date()
                t = dt.datetime.strptime(hhmm_str, "%H-%M").time()

            except ValueError :

                continue

            ts = dt.datetime.combine(d, t)

            if (best_ts is None) or ts > best_ts :

                best_ts = ts
                best_path = Path(entry.path)

    log(f"[*] Search most recent file done in {time.time() - start:.2f} seconds")
    
    return best_path


def date_cast_expr_from_utf8 (
        
        col: str,
        *,
        to_datetime: bool = False,
        formats: list[str] | None = None,

        allow_us_mdy: bool = False,
        enable_excel_serial: bool = True,

    ) -> pl.Expr:
    """
    Parse messy date/datetime strings with multiple formats + Excel-serial fallback.
    Works for ANY column name; returns an Expr aliasing `col`.
    """
    fmts = formats or [

        "%d/%m/%Y",      # 30/10/2025
        "%Y-%m-%d",      # 2025-10-30
        "%b %e, %Y",     # Oct 30, 2025 (space-padded day)
        "%b %-d, %Y",    # Oct 9, 2025 (no zero-pad)
        "%Y.%m.%d",      # 2025.10.30
    
    ]
    
    if allow_us_mdy :
        fmts.append("%m/%d/%Y")  # enable only if you truly have US dates

    txt = (

        pl.col(col).cast(pl.Utf8, strict=False)
        .str.replace_all("\u00A0", " ")         # NBSP → space
        .str.replace_all(r"[ ]{2,}", " ")
        .str.strip_chars()

    )

    parsed = [

        txt.str.strptime(
        
            pl.datetime if to_datetime else pl.Date,
            format=f,
            strict=False,
            exact=False
        
        )
        for f in fmts
    ]

    out = parsed[0]

    for p in parsed[1:] :
        out = out.fill_null(p)

    if enable_excel_serial :

        excel_fallback = (

            pl.when(pl.col(col).cast(pl.Float64, strict=False).is_not_null())
            .then(
                (pl.datetime(1899, 12, 30) + pl.duration(
                    days=pl.col(col).cast(pl.Float64, strict=False).round(0).cast(pl.Int64)
                )).cast(pl.Datetime if to_datetime else pl.Date, strict=False)
            )
        )
        out = out.fill_null(excel_fallback)

    return out.alias(col)


def numeric_cast_expr_from_utf8 (
        
        col : str,
        target_dtype : pl.PolarsDataType,

        decimal : str = ".",          # "." for 1,234.56  / "," for 1.234,56
        int_rounding : str = "nearest"  # "nearest" | "floor" | "ceil" | "truncate"

    ) -> pl.Expr:
    """
    Clean common artefacts (spaces, NBSP, %, currency, parentheses negativity, thousands sep)
    and cast to Float/Int as requested by target_dtype.
    Example handled: "-123,254.58" -> -123254.58 (decimal=".")
    """
    e = pl.col(col).cast(pl.Utf8, strict=False)

    # Common cleaning pipeline on strings
    e = (
        
        #.cast(pl.Utf8, strict=False)
        e.str.strip_chars()
        .str.replace_all(r"\s+", "")              # remove all spaces (incl NBSP)
        .str.replace_all(r"[%€$£]", "")           # drop currency/percent
        .str.replace_all(r"\(([^)]+)\)", r"-$1")  # (123) -> -123
        
    )

    if decimal == ".":
        # strip thousands separators commonly used with dot-decimal
        e = (e
             .str.replace_all(",", "")              # 1,234.56 -> 1234.56
             )
        
    # decimal point is already "."
    elif decimal == "," :

        # EU style: 1.234,56 -> 1234.56
        e = (e
             .str.replace_all(r"\.", "")           # remove thousands dots
             .str.replace_all(",", ".")            # comma decimal -> dot
             )
    
    else :
        raise ValueError('decimal must be "." or ","')

    # First cast to float to normalize; then handle integers if needed
    e_float = e.cast(pl.Float64, strict=False)

    # Decide on integer vs float target
    if isinstance(target_dtype, pl.Float32.__class__) or target_dtype in (pl.Float32, pl.Float64) :
        return e_float.alias(col)

    # Integer targets (Int*/UInt*)
    if int_rounding == "nearest" :
        e_int_base = e_float.round(0)

    elif int_rounding == "floor" :
        e_int_base = e_float.floor()

    elif int_rounding == "ceil" :
        e_int_base = e_float.ceil()

    elif int_rounding == "truncate" :
        # toward zero
        e_int_base = pl.when(e_float < 0).then(e_float.ceil()).otherwise(e_float.floor())
    
    else :
        raise ValueError('int_rounding must be "nearest" | "floor" | "ceil" | "truncate"')

    return e_int_base.cast(target_dtype, strict=False).alias(col)


def exclude_token_cols_from_df(dataframe : pl.DataFrame, column : str, token : str):
    """
    Retourne un DataFrame sans les colonnes contenant un token spécifique dans leur nom.
    
    Parameters:
    - df : pd.DataFrame — le DataFrame d'origine
    - token : str — le mot ou token à exclure des noms de colonnes
    
    Returns:
    - pd.DataFrame — un DataFrame avec les colonnes filtrées
    """
    regex = rf"(?i){token}"

    filtered_cols = dataframe.filter(

        ~pl.col(column).str.contains(regex)

    )
    return filtered_cols


def filter_token_col_from_df (dataframe : pl.DataFrame, column : str, token : str) :
    """
    Filters rows in a dataframe where a specific column contains a token (case-insensitive).

    Args:
        dataframe (pl.DataFrame): Input dataframe.
        column (str): Column name to apply filter.
        token (str): Token to search for.

    Returns:
        clean_df (pl.DataFrame) : Filtered dataframe.
    """
    if token is None or column is None :
        return dataframe
    
    regex = rf"(?i){token}"

    clean_df = dataframe.filter(

        pl.col(column).str.contains(regex)

    )

    return clean_df


def filter_groupby_col_from_df (dataframe : pl.DataFrame, colum : str) :
    """
    Sorts the dataframe by a given column.
    (Note: Despite the function name, this does not perform a groupby operation.)

    Args:
        dataframe (pl.DataFrame): Input dataframe.
        colum (str): Column to sort by.

    Returns:
        pl.DataFrame: Sorted dataframe.
    """
    grouped_df = dataframe.sort(
        colum
    )

    return grouped_df


def format_numeric_columns_to_string(
        
        df: pl.DataFrame,
        columns: Optional[List[str]] = None,
        decimals: int = 2,
        thousand_sep: str = ",",
        decimal_sep: str = ".",
    
    ) -> pl.DataFrame:
    """
    Convert numeric columns into human-readable formatted strings.
    Example: 1234567.89 -> "1,234,567.89"

    If `columns=None`, all numeric columns are formatted.
    """
    # 1. Detect numeric columns if none provided
    if columns is None:
    
        numeric_types = {

            pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Int128,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64,
        }

        columns = [c for c, t in df.schema.items() if t in numeric_types]

    fmt = f"{{:,.{decimals}f}}"  # Python formatting

    exprs = []
    for col in columns :

        exprs.append(
        
            pl.col(col)
            .cast(pl.Float64, strict=False)        # ensure float
            .map_elements(
        
                lambda x, f=fmt: (
                    f.format(x)
                    .replace(",", thousand_sep)
                    .replace(".", decimal_sep)
                    if x is not None else None
                ),
        
                return_dtype=pl.Utf8,
            )
            .alias(col)
        )

    return df.with_columns(exprs)


def normalize_fx_dict (raw_fx : Optional[Dict[str, float]] = None, ends_with : str = "-X", start_with = "EUR") -> Optional[Dict[str, float]] :
    """
    Normalize Yahoo Finance FX tickers into { 'USD': 1.10, 'CHF': 0.95, ... }
    Meaning: each value is the amount of that currency per 1 EUR.

    Examples:
        {'EURUSD=X': 1.1, 'EURCHF=X': 0.95} → {'USD': 1.1, 'CHF': 0.95, 'EUR': 1.0}
    """
    normalized : Dict[str, float] = {"EUR": 1.0}

    for pair, val in raw_fx.items() :

        if pd.isna(val) :
            # Normally never in this case.
            continue

        name = str(pair).upper()

        if name.endswith(ends_with) :
            name = name[:-2]  # remove trailing =X

        if name.startswith(start_with) and len(name) >= 6 :

            ccy = name[3:6]
            normalized[ccy] = float(val)

    print("\n[*] Normalizing FX values")

    return normalized


def colorize_dataframe_positive_negatif_vals (
        
        dataframe : Optional[pl.DataFrame],
        columns : Optional[List[str]] = None,
    
    ) :
    """
    Docstring for colorize_dataframe_positive_negatif_vals
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    """
    dataframe = dataframe.to_pandas()

    def colorize (val) :
        """
        Docstring for colorize
        
        :param val: Description
        """
        if pd.isna(val):
            return ""
        
        return "color: green;" if float(val) >= 0 else "color: red;"

    styled = (
        dataframe
        .style
        .applymap(colorize, subset=columns)
        .set_table_styles(
            [
                {"selector": "th", "props": [("text-align", "center")]},
                {"selector": "td", "props": [("text-align", "center")]},
            ]
        )
        .set_properties(**{"text-align": "center"})
    )
    

    return styled



