import os, re
import hashlib
from pathlib import Path
import time
import polars as pl
import datetime as dt

from typing import Dict, List, Optional, Tuple, Any

from src.utils.logger import log


def date_to_str (date : str | dt.datetime = None, format : str = "%Y-%m-%d") -> str :
    """
    Convert a date or datetime object to a string in specific ("YYYY-MM-DD" default) format.

    Args:
        date (str | datetime): The input date.
        format (str) : The string format for the date

    Returns:
        str: Date string in "YYYY-MM-DD" format.
    """
    if date is None :

        return dt.datetime.now().strftime(format)

    if isinstance(date, str) :

        try :

            # try to parse common formats
            parsed = dt.datetime.fromisoformat(date.strip())
            return parsed.strftime(format)
        
        except ValueError :
            return date.strip()  # fallback: assume already good
    
    # works for both date & datetime
    if isinstance(date, dt.date) :

        return date.strftime(format)
    

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