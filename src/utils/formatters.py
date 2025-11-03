from __future__ import annotations

import os
import re
import time
import hashlib
import calendar

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