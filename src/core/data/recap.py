from __future__ import annotations

import os
import re
import html
import math
import polars as pl
import datetime as dt

from html import unescape

from typing import Any, List, Optional, Dict, Tuple, Mapping, Callable, Iterable

from src.config.paths import TREADE_RECAP_DATA_RAW_DIR_ABS_PATH
from src.config.parameters import (
    TRADE_RECAP_RAW_FILE_REGEX, TRADE_RECAP_MIN_COLUMNS, TRADE_RECAP_MIN_COLUMNS, UBS_TRADE_RECAP_NUMBER,
    FUND_MAP, UBS_ENSURE_COLUMNS, TRADE_RECAP_EMAIL_DEFAULT_BODY_INTRO, TRADE_RECAP_EMAIL_DEFAULT_FX_CC,
    TRADE_RECAP_EMAIL_DEFAULT_FX_TO, TRADE_RECAP_EMAIL_BODY_NO_TRADES, TRADE_RECAP_EMAIL_DEFAULT_MASTER_CC,
    TRADE_RECAP_EMAIL_DEFAULT_MASTER_TO, TRADE_RECAP_EMAIL_DEFAULT_OTC_CC, TRADE_RECAP_EMAIL_DEFAULT_OTC_TO,
    TRADE_RECAP_EMAIL_COLUMNS, TRADE_RECAP_TH_STYLE, TRADE_RECAP_NUM_TYPES, TRADE_RECAP_TABLE_STYLE,
    TRADE_RECAP_TD_NUM_STYLE, TRADE_RECAP_TD_STYLE
    
    )
from src.utils.data_io import load_excel_to_dataframe
from src.utils.formatters import str_to_date, str_to_datetime
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
            print()
            #dataframe = dataframe.select(list(schema_overrides.keys()))

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
        regex : Optional[re.Pattern] = None,

        format : str = "%Y-%m-%d",
        timestamp_format : str = "%Y_%m_%dT%H_%M",

    ) -> Tuple[Optional[str], Optional[str]] :
    """
    Docstring for find_most_recent_file_by_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param dir_abs_path: Description
    :type dir_abs_path: Optional[str]
    :param regex: Description
    :type regex: Optional[re.Pattern]
    """
    date = str_to_date(date, format) if date is not None else None

    dir_abs_path = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path
    regex = TRADE_RECAP_RAW_FILE_REGEX if regex is None else regex

    if not os.path.isdir(dir_abs_path) :
        return None, None
    
    # Keep only files matching the selected trade date
    # value = (as_of_dt, mtime, filename)
    best_file : Optional[Tuple[dt.datetime, str]] = None

    with os.scandir(dir_abs_path) as it :
        
        for entry in it :

            if not entry.is_file() :
                continue
            
            m = regex.match(entry.name)

            if not m :
                continue

            trade_date_str, timestamp_datetime_str = m.groups()

            trade_date = str_to_date(trade_date_str, format)
            timestamp_datetime = str_to_datetime(timestamp_datetime_str, timestamp_format)

            if trade_date != date :
                continue
            
            candidate = (timestamp_datetime, entry.name)

            if best_file is None or candidate[0] > best_file[0] :
                best_file = candidate


    if best_file is None :
        return None, None
    
    print(best_file)
    
    return best_file[0], best_file[1]



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



def apply_otc_fx_logic_to_trade(
        
        dataframe: Optional[pl.DataFrame],
        md5: Optional[str] = None,
        columns: Optional[List] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]]:
    """
    Applies OTC/FX/LISTED labelling logic to trades based on asset class and instrument type.

    Rules:
        - FX + instrument type in (Spot, Forward, Swap) → "FX", else → "OTC"
        - EQ + trade description or instrument type contains "LISTED" → "LISTED", else → "OTC"
        - COMMODITY → "OTC"
        - Else → "LISTED"

    :param dataframe: Input Polars DataFrame
    :param md5: Optional md5 hash passthrough
    :param columns: Optional list of columns to use (default applied if None)
    :return: Tuple of (labelled DataFrame or None, md5 or None)
    """
    if dataframe is None or dataframe.is_empty():
        return dataframe, md5

    # --- Guard: Label must exist
    if "Label" not in dataframe.columns:
        dataframe = dataframe.with_columns(pl.lit("").cast(pl.Utf8).alias("Label"))

    # --- Guard: assetClass must exist
    if "assetClass" not in dataframe.columns:
        print("\n[-] No Asset Class present in the dataframe, skipping...")
        return dataframe, md5

    # --- Skip if any label is already populated
    label_is_populated = (
        pl.col("Label").fill_null("").cast(pl.Utf8).str.strip_chars() != ""
    )
    if dataframe.select(label_is_populated.any()).item():
        return dataframe, md5

    # --- Safely resolve optional columns
    for col_name in ("tradeLegCode", "tradeDescription") :

        if col_name not in dataframe.columns :
            dataframe = dataframe.with_columns(pl.lit("").cast(pl.Utf8).alias(col_name))

    # --- Resolve instrument type (prefer instrument.instrumentType, fallback to fields.instrumentType)
    if "instrument.instrumentType" in dataframe.columns :
        raw_instrument_type = pl.col("instrument.instrumentType")

    elif "fields.instrumentType" in dataframe.columns :
        raw_instrument_type = pl.col("fields.instrumentType")

    else :
        raw_instrument_type = pl.lit("")

    instrument_type  = raw_instrument_type.fill_null("").cast(pl.Utf8).str.to_uppercase()
    trade_description = pl.col("tradeDescription").fill_null("").cast(pl.Utf8).str.to_uppercase()
    ac               = pl.col("assetClass").fill_null("").cast(pl.Utf8).str.to_uppercase()

    # --- Conditions
    is_fx        = ac == "FX"
    is_eq        = ac == "EQ"
    is_commodity = ac == "COMMODITY"

    fx_instrument = instrument_type.is_in(["SPOT", "FORWARD", "SWAP"])
    has_listed    = (
        trade_description.str.contains("LISTED")  # tradeDescription column
        | instrument_type.str.contains("LISTED")  # instrument.instrumentType column (already uppercased)
    )

    has_stock    = (
        trade_description.str.contains("STOCK")  # tradeDescription column
        | instrument_type.str.contains("STOCK")  # instrument.instrumentType column (already uppercased)
    )


    # --- 1) Compute label per leg (mirrors the rule image exactly)
    leg_label_expr = (
        pl.when(is_fx & fx_instrument).then(pl.lit("FX"))
          .when(is_fx & ~fx_instrument).then(pl.lit("OTC"))
          .when(is_eq & (has_listed | has_stock)).then(pl.lit("LISTED"))
          .when(is_eq & (~has_listed & ~has_stock)).then(pl.lit("OTC"))
          .when(is_commodity).then(pl.lit("OTC"))
          .otherwise(pl.lit("LISTED"))  # default per the rules
    )

    dataframe = dataframe.with_columns(leg_label_expr.alias("_leg_label"))

    # --- 2) Consolidate at the tradeId level
    # Priority: OTC > FX > LISTED
    if "tradeId" in dataframe.columns:
        has_otc = (pl.col("_leg_label") == "OTC").any().over("tradeId")
        has_fx  = (pl.col("_leg_label") == "FX").any().over("tradeId")

        trade_label_expr = (
            pl.when(has_otc).then(pl.lit("OTC"))
              .when(has_fx).then(pl.lit("FX"))
              .otherwise(pl.lit("LISTED"))
              .alias("Label")
        )
        dataframe = dataframe.with_columns(trade_label_expr).drop("_leg_label")
    else:
        # Fallback if no tradeId
        dataframe = dataframe.with_columns(pl.col("_leg_label").alias("Label")).drop("_leg_label")

    return dataframe, md5



def reconcile_edited_with_original (
        
        df_edited : pl.DataFrame,
        df_original : pl.DataFrame,

        leg_id_col : str = "tradeLegId",
        editable_cols : Optional[List[str]] = None,

    ) -> pl.DataFrame :
    """
    
    """
    editable_cols = TRADE_RECAP_MIN_COLUMNS if editable_cols is None else editable_cols

    df_edited = df_edited.with_columns(pl.col(leg_id_col).cast(pl.Utf8, strict=False))
    df_original = df_original.with_columns(pl.col(leg_id_col).cast(pl.Utf8, strict=False))

    if leg_id_col not in df_edited.columns:
        # Nothing to match on — return original untouched
        return df_original
    
    kept_ids = df_edited[leg_id_col].drop_nulls().unique()
    base = df_original.filter(pl.col(leg_id_col).is_in(kept_ids))

    edit_cols_present = [c for c in editable_cols if c in df_edited.columns and c != leg_id_col]
    patch = df_edited.select([leg_id_col] + edit_cols_present)

    # Drop editable cols from base so join won't duplicate them
    cols_to_drop = [c for c in edit_cols_present if c in base.columns]
    if cols_to_drop:
        base = base.drop(cols_to_drop)

    reconciled = base.join(patch, on=leg_id_col, how="left")

    # restore order
    order = (df_edited.select(leg_id_col).with_row_index("__order"))
    reconciled = (reconciled.join(order, on=leg_id_col, how="left").sort("__order", nulls_last=True).drop("__order"))

    if "Label" not in reconciled.columns:
        reconciled = reconciled.with_columns(pl.lit("").alias("Label"))

    reconciled = reconciled.with_columns(
        pl.col("Label").fill_null("").cast(pl.Utf8)
    )

    # ── Enforce dtypes on editable cols ──────────────────────────────────────
    cast_exprs = [

        pl.col(col).cast(dtype, strict=False).alias(col)
        for col, dtype in editable_cols.items()
        if col in reconciled.columns
    ]

    if cast_exprs:
        reconciled = reconciled.with_columns(cast_exprs)

    return reconciled


def generate_final_trade_recap_report (
        
        dataframe : Optional[pl.DataFrame] = None,
        file_raw : Optional[str] = None,

        ensure_columns : Optional[Dict] = None,
        fund_map : Optional[Dict] = None,
        dictionnary_ubs : Optional[Dict] = None,

    ) :
    """
    
    """
    fund_map = FUND_MAP if fund_map is None else fund_map
    dictionnary_ubs = UBS_TRADE_RECAP_NUMBER if dictionnary_ubs is None else dictionnary_ubs
    ensure_columns = UBS_ENSURE_COLUMNS if ensure_columns is None else ensure_columns

    dataframe = dataframe.with_columns(

        pl.when(
            pl.col("bookName")
            .cast(pl.Utf8, strict=False)
            .str.strip_chars()
            .str.to_uppercase()
            .str.starts_with("HV")
        )
        
        .then(pl.lit(fund_map.get("HV")))
        .when(
            pl.col("bookName")
            .cast(pl.Utf8, strict=False)
            .str.strip_chars()
            .str.to_uppercase()
            .str.starts_with("WR_")
        )
        .then(pl.lit(fund_map.get("WR")))
        .otherwise(None)
        .alias("Fund Name")

    )

    df = compute_premieum_in_pctg(df, ensure_columns)

    ensure_columns_ubs = "parentPortfolioName"

    df = ubs_portfolio_number(df, ensure_columns_ubs, dictionnary_ubs)
    
    # Drop structures
    df = df.unique("tradeLegId", maintain_order=True)

    # Drop remaining Struct/List[Struct] to keep Excel wide sheet clean
    df = drop_struct_and_liststruct_columns(df, verbose=True)

    return df



def create_email_item_recap (
        
        to_email : Optional[str] = None,
        cc_email : Optional[str] = None,

        from_email : Optional[str] = None,

        subject : str = None,
        dataframe : str = None,

        attachment_files = None,
        display = False

    ) :
    """
    """
    dataframe = None

    return None,



def compute_premieum_in_pctg (dataframe : pl.DataFrame, columns : List[str]) :
    """
    
    Docstring for compute_premieum_in_pctg
    
    :param dataframe: Description
    :type dataframe: pl.Dataframe
    :param columns: Description
    :type columns: List[str]
    """

    if dataframe.is_empty() or dataframe is None :
        return None
    
    if columns is None or len(columns) == 0 :
        return dataframe
    
    # Let's ensure the columns existent, otherwise we have to continue
    for column in columns :
        
        if column not in dataframe.columns :
            # Continue (Not all columns)
            return dataframe
        
    # Required columns check
    if any(c not in dataframe.columns for c in columns) :
        return dataframe

    # --- helper: robust numeric casting ---
    EMPTY = ["", " ", "-", " - ", "–", "—", "nan", "none", "null", "n/a", "na"]

    def clean_str(expr : pl.Expr) -> pl.Expr :
        """
        """
        s = expr.cast(pl.Utf8, strict=False).str.strip_chars().str.to_lowercase()

        return pl.when(s.is_in(EMPTY)).then(None).otherwise(s)


    def to_float(expr: pl.Expr) -> pl.Expr :
        
        s = expr.cast(pl.Utf8, strict=False).str.strip_chars().str.to_lowercase()
        s = s.str.replace_all(r"[,\s]", "")  # remove commas/spaces
        s = pl.when(s.is_in(EMPTY)).then(None).otherwise(s)

        return s.cast(pl.Float64, strict=False)


    def valid_num(x: pl.Expr) -> pl.Expr :
        return x.is_not_null() & (x != 0)


    prem_ccy = clean_str(pl.col("premium.currency"))
    put_ccy  = clean_str(pl.col("fields.PutCurrency"))
    call_ccy = clean_str(pl.col("fields.CallCurrency"))

    premium_amt = to_float(pl.col("premium.amount"))
    put_not     = to_float(pl.col("fields.PutNotional"))
    call_not    = to_float(pl.col("fields.CallNotional"))
    instr_not   = to_float(pl.col("instrument.notional"))

    prem_ok  = valid_num(premium_amt)
    put_ok   = valid_num(put_not)
    call_ok  = valid_num(call_not)
    instr_ok = valid_num(instr_not)

    # If currency matches Put -> prefer PutNotional else fallback instrument
    put_choice = (
        pl.when(prem_ccy == put_ccy)
        .then(pl.when(put_ok).then(put_not).otherwise(pl.when(instr_ok).then(instr_not).otherwise(None)))
        .otherwise(None)
    )

    # If currency matches Call -> prefer CallNotional else fallback instrument
    call_choice = (
        pl.when(prem_ccy == call_ccy)
        .then(pl.when(call_ok).then(call_not).otherwise(pl.when(instr_ok).then(instr_not).otherwise(None)))
        .otherwise(None)
    )

    # If no match Put/Call -> use instrument.notional (universal fallback)
    chosen_notional = pl.coalesce([put_choice, call_choice, pl.when(instr_ok).then(instr_not).otherwise(None)])

    premium_pct = (
        pl.when(prem_ok & valid_num(chosen_notional))
        .then((premium_amt / chosen_notional) * 100)   # PREMIUM / NOTIONAL
        .otherwise(None)
    )
 
    dataframe = dataframe.with_columns(
        [
            pl.col("premium.currency").alias("Premium Style"),
            pl.when(pl.col("assetClass") == "FX").then(premium_pct).otherwise(None).alias("Premium in %"),
        ]
    )

    return dataframe



def ubs_portfolio_number (dataframe : pl.DataFrame, column: str, dictionnary : Dict[str, int]) :
    """
    Docstring for ubs_portfolio_number
    
    :param dataframe: Description
    :type dataframe: pl.DataFrame
    :param columns: Description
    :type columns: List[str]
    :param dictionnary: Description
    :type dictionnary: Dict[str, int]
    """
    if dataframe is None or dataframe.is_empty() :
        return None
    
    if column is None or len(column) <= 0 :
        return dataframe
    
    new_column_name = f"UBS Portfolio No"

    dataframe = dataframe.with_columns(
        pl.col(column).map_elements(lambda x: dictionnary.get(x, None), return_dtype=pl.Int64).alias(new_column_name)
    )

    return dataframe


def drop_struct_and_liststruct_columns (df : pl.DataFrame) -> pl.DataFrame :
    """
    Drop columns whose dtype is `Struct` or `List[Struct]`.

    This uses dtype-based selection (robust across Polars versions).

    Args:
        df: Input DataFrame (may be empty).
        verbose: If True, log dropped column names.

    Returns:
        A new DataFrame with selected columns removed (or `df` unchanged).
    """
    if df is None or df.is_empty() :
        return df
    
    # Select column names by dtype; safer than manual dtype comparisons
    struct_cols = df.select(pl.col(pl.Struct)).columns
    list_struct_cols = df.select(pl.col(pl.List(pl.Struct))).columns
    to_drop = list(dict.fromkeys(struct_cols + list_struct_cols))
        
    return df.drop(to_drop) if to_drop else df





def generate_html_template_body (
        
        dataframe: pl.DataFrame,
        *,
        intro: Optional[str] = None,
        caption: str = "Trades Recap",
        max_rows: int = 2000,
        zebra: bool = True,

        email_columns: Optional[Dict[str, pl.DataType]] = None,
        keep_only_defined: bool = True,
        exclude_asset_classes : Optional[List[str]] = None,
    
    ) -> str:
    """
    Build the HTML block (intro paragraph + table) from a Polars DF.
    """
    intro = TRADE_RECAP_EMAIL_DEFAULT_BODY_INTRO if intro is None else intro
    email_columns = TRADE_RECAP_EMAIL_COLUMNS if email_columns is None else email_columns

    if exclude_asset_classes:
        dataframe = dataframe.filter(~pl.col("assetClass").is_in(exclude_asset_classes))

    dataframe = dataframe.unique("tradeLegId", maintain_order=True)

    recap_df = apply_email_recap_columns(
        dataframe,
        columns_order=email_columns,
        keep_only_defined=keep_only_defined,
    )

    #recap_df = build_recap_from_roots(dataframe, roots=None)
    
    html_block = build_email_body_from_df(
    
        recap_df,
        intro_text=intro,
        caption=caption,
        max_rows=max_rows,
        zebra=zebra,
    
    )
    
    html_block = unescape(html_block)
    
    return html_block



def apply_email_recap_columns (
        
        dataframe : Optional[pl.DataFrame] = None,
        columns_order : Optional[Dict[str, pl.DataType]] = None,
        keep_only_defined : bool = True,

    ) -> pl.DataFrame :
    """
    Reorder columns (and optionally keep only) for email body.
    Missing columns are created as null with the provided dtype.
    Extra columns are dropped if keep_only_defined=True.
    """
    if dataframe is None or dataframe.is_empty() :
        return pl.DataFrame()

    if columns_order is None :
        return dataframe

    expected_cols = list(columns_order.keys())
    existing = set(dataframe.columns)

    # create missing columns
    missing_expr = [
        pl.lit(None).cast(dtype).alias(col)
        for col, dtype in columns_order.items()
        if col not in existing
    ]

    if missing_expr :
        dataframe = dataframe.with_columns(missing_expr)

    # reorder + optionally drop others
    if keep_only_defined :
        dataframe = dataframe.select(expected_cols)
    else :
        rest = [c for c in dataframe.columns if c not in expected_cols]
        dataframe = dataframe.select(expected_cols + rest)

    return dataframe



def build_email_body_from_df(
        
        df: pl.DataFrame,
        *,
        intro_text: str = "Please find a quick recap below. Full file attached.",
        caption: str | None = None,
        max_rows: int = 1000,
        zebra: bool = False,
        column_formatters : Optional[Mapping[str, callable]] = None,

    ) -> str:
    """
    Build a full HTML fragment (paragraph + table) from a Polars DataFrame.
    This returns a string ready to be embedded into an email body (in outlook.py)
    or into any HTML page.

    Note: does NOT include <html>/<body> wrapper to let callers merge with signatures.
    """
    table_html = df_to_html_table(
        df,
        max_rows=max_rows,
        caption=caption,
        zebra=zebra,
        column_formatters=column_formatters,
    )

    return f"{(intro_text)}<p>{table_html}<p>"


def df_to_html_table(
        
        df: pl.DataFrame,
        *,
        max_rows: int = 1000,
        caption: str | None = None,
        zebra: bool = False,
        column_formatters: Optional[Mapping[str, callable]] = None,
        
        autosize: bool = True,
        min_col_ch: int = 6,
        max_col_ch: int = 60,
        truncate_text_at: int | None = None,
        min_table_px: Optional[int] = 1200,

    ) -> str:
    """
    Convert a Polars DataFrame into an HTML <table> string.

    Args:
        max_rows: limit to the first N rows
        caption: optional <caption> content
        zebra: add manual zebra striping (no CSS selectors)
        column_formatters: optional {column_name: fn(value)->str} override
    """
    if df.is_empty() :
        return "<p><em>No rows.</em></p>"

    headers = df.columns
    data = df.head(max_rows).iter_rows()  # tuple rows (fast)
    
    rows = list(df.head(max_rows).iter_rows())
    schema = df.schema
    
    num_idx = {i for i, h in enumerate(headers) if schema[h] in TRADE_RECAP_NUM_TYPES}

    # Prepare per-column formatters
    fmt_map = {c: _default_fmt for c in headers}

    if column_formatters :

        for k, fn in column_formatters.items() :
        
            if k in fmt_map and callable(fn) :
                fmt_map[k] = fn

    colgroup_html = ""

    if autosize:
    
        widths_ch = _estimate_col_widths_in_ch(
            df,
            headers=headers,
            schema=schema,
            data_rows=rows,
            column_formatters=fmt_map,
            min_ch=min_col_ch,
            max_ch=max_col_ch,
        )

        # Use table-layout:auto and prefer width hints via colgroup
        colgroup = ['<colgroup>']
        
        for w in widths_ch :
            colgroup.append(f'<col style="width:{w}ch;">')
        
        colgroup.append('</colgroup>')
        colgroup_html = "".join(colgroup)
    
    table_style = TRADE_RECAP_TABLE_STYLE

    if min_table_px :
        table_style = table_style + f"min-width:{min_table_px}px;"  # Outlook-friendly

    parts: List[str] = []
    parts.append('<table role="presentation" style="' + TRADE_RECAP_TABLE_STYLE + '">')

    # Insert colgroup right after <table> for width hints
    if colgroup_html :
        parts.append(colgroup_html)

    if caption :
        parts.append(f"<caption>{html.escape(caption)}</caption>")

    # THEAD
    parts.append("<thead><tr>")
    for h in headers :
        parts.append(f'<th style="{TRADE_RECAP_TH_STYLE}">{html.escape(h)}</th>')
    
    parts.append("</tr></thead>")

    # TBODY
    parts.append("<tbody>")
    odd = False
    
    for row in data :

        row_style = ""
        
        if zebra :

            odd = not odd
            
            if odd :
                row_style = ' style="background:#FAFAFA;"'
        
        parts.append(f"<tr{row_style}>")
        
        for i, v in enumerate(row) :

            col = headers[i]
            
            txt = fmt_map[col](v)
            txt = html.escape("" if txt is None else str(txt), quote=True)
            
            style = TRADE_RECAP_TD_NUM_STYLE if i in num_idx else TRADE_RECAP_TD_STYLE
            
            parts.append(f'<td style="{style}">{txt}</td>')
        
        parts.append("</tr>")
    
    parts.append("</tbody></table>")

    if df.height > max_rows:
        parts.append(f"<p>Showing {max_rows} of {df.height} rows.</p>")

    return "".join(parts)

def _default_fmt (v : Any) -> str :
    """
    Default cell text formatting before escaping.
    """
    if v is None :
        return ""
    
    if isinstance(v, float) :

        if math.isnan(v) :
            return ""
        
        return f"{v:.6g}"  # tweak precision as needed
    
    if isinstance(v, (dt.datetime, dt.date)) :
        return v.isoformat()
    

def _estimate_col_widths_in_ch (
        
        df: pl.DataFrame,
        *,
        headers: List[str],
        schema: dict[str, pl.DataType],
        data_rows: Iterable[tuple],
        column_formatters: Mapping[str, Callable[[Any], str]] | None,
        min_ch: int = 6,
        max_ch: int = 60,
    
    ) -> List[int] :
    """
    Very simple heuristic:
      width = clamp( max(len(header), max(len(formatted cell) for sampled rows)) )
    """
    # Prepare per-column formatters
    fmt_map: dict[str, Callable[[Any], str]] = {c: _default_fmt for c in headers}

    if column_formatters :
    
        for k, fn in column_formatters.items() :

            if k in fmt_map and callable(fn) :
                fmt_map[k] = fn

    # Initialize with header lengths
    max_lens = [len(h) for h in headers]

    # Sample rows to refine widths
    for row in data_rows :

        for i, v in enumerate(row) :

            col = headers[i]
            txt = fmt_map[col](v)
            
            # Use the *visible* length before HTML escaping; good enough for ch units.
            L = len("" if txt is None else str(txt))
            
            if L > max_lens[i] :
                max_lens[i] = L

    # Clamp into a reasonable range to avoid wild widths
    widths = [max(min_ch, min(max_ch, L)) for L in max_lens]

    return widths