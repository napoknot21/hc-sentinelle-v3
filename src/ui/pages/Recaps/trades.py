from __future__ import annotations

import io
import datetime as dt
from typing import Optional, Tuple, List

import polars as pl
import pandas as pd
import streamlit as st

from src.utils.formatters import str_to_date
from src.ui.components.text import center_h5
from src.core.api.recap import trade_recap_launcher
from src.core.data.recap import (
    read_trade_recap_by_date, find_most_recent_file_by_date, clean_structure_from_dataframe,
    apply_user_review_defaults, apply_otc_fx_logic_to_trade,
)

KEY_DF        = "dataframe_recap_daily"
KEY_DF_BASE   = "dataframe_recap_daily_base"        # stable base passed to data= – never mutated during editing
KEY_MD5       = "dataframe_md5_recap_daily"
KEY_EDITOR    = "dataframe_editor_recap_daily"      # base name – never used as widget key directly
KEY_EDITOR_GEN = "dataframe_editor_recap_daily_gen" # int counter – bump to reset the editor widget
KEY_VALIDATED = "dataframe_recap_daily_validated"
KEY_FILE      = "dataframe_recap_daily_filename"


def _editor_widget_key () -> str :
    """
    Return the current widget key for st.data_editor.
    Changing the generation counter produces a new key, which forces Streamlit
    to mount a fresh widget with no stale diff state – without us ever writing
    to st.session_state[widget_key] directly.
    """
    gen = st.session_state.get(KEY_EDITOR_GEN, 0)
    return f"{KEY_EDITOR}__{gen}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_row_key_expr (cols: List[str]) -> pl.Expr :
    return pl.concat_str([pl.col(c).fill_null("").cast(pl.Utf8) for c in cols], separator="|")


def polars_to_excel_bytes (dataframe: pl.DataFrame, sheet_name: str = "Sheet1") -> bytes :
    """
    Convert a Polars DataFrame to Excel bytes.
    """
    df_pd = dataframe.to_pandas()

    with io.BytesIO() as output :

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer :
            df_pd.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return output.getvalue()


def generate_email_draft_bytes (
        
        df    : pl.DataFrame,
        label : str = "MASTER",
        date  : Optional[str | dt.datetime | dt.date] = None,
    
    ) -> bytes :
    """
    Generate a plain-text email draft from a recap dataframe.
    Extend with your own template logic.
    """
    date_str  = str(date) if date is not None else "N/A"
    row_count = df.height if df is not None else 0

    lines = [
        f"Subject: Trade Recap – {label} – {date_str}",
        "",
        "Dear Team,",
        "",
        f"Please find below the {label} trade recap for {date_str}.",
        f"Total trades: {row_count}",
        "",
    ]

    if df is not None and not df.is_empty() :
        lines.append("\t".join(df.columns))
        lines.append("-" * 80)

        for row in df.to_dicts() :
            lines.append("\t".join(str(v) if v is not None else "" for v in row.values()))

    lines += ["", "Best regards,", "Trade Operations"]

    return "\n".join(lines).encode("utf-8")


def drop_temp_cols_master (df : pl.DataFrame, drop_cols: Optional[List[str]] = None) -> pl.DataFrame :
    """
    Drop temp columns from master after validation (Label).
    """
    if df is None or df.is_empty() :
        return pl.DataFrame()

    drop_cols = ["Label"] if drop_cols is None else drop_cols
    existing  = [c for c in drop_cols if c in df.columns]
    
    return df.drop(existing) if existing else df


def apply_labels_from_light_to_complete (
        
        df_light    : pl.DataFrame,
        df_complete : pl.DataFrame,
        label_col   : str = "Label",
    
    ) -> pl.DataFrame :
    """
    Transfer Label from df_light to df_complete using a key built from shared columns.
    Best-effort: if there are duplicates on the key, keep last.
    """
    if df_light is None or df_light.is_empty() :
        return df_complete
    
    if df_complete is None or df_complete.is_empty() :
        return df_complete

    common = [c for c in df_light.columns if c in df_complete.columns and c != label_col]
    
    if not common :

        n           = min(df_light.height, df_complete.height)
        light_slice = df_light.head(n).select([label_col])
        
        comp_slice  = df_complete.head(n).with_columns(
            light_slice.get_column(label_col).alias(label_col)
        )

        return pl.concat([comp_slice, df_complete.slice(n, df_complete.height - n)], how="vertical")

    k_expr = _build_row_key_expr(common)

    light_map = (
        df_light
        .with_columns(k_expr.alias("__k"))
        .select(["__k", label_col])
        .unique(subset=["__k"], keep="last")
    )

    out = (
        df_complete
        .with_columns(k_expr.alias("__k"))
        .join(light_map, on="__k", how="left", suffix="_map")
        .with_columns(
            pl.coalesce([pl.col(f"{label_col}_map"), pl.col(label_col)]).alias(label_col)
        )
        .drop(["__k", f"{label_col}_map"])
    )
    return out


def ensure_session_keys (
        
        dataframe  : Optional[pl.DataFrame] = None,
        md5        : Optional[str]           = None,
        date       : Optional[str | dt.datetime | dt.date] = None,
        filename   : Optional[str] = None,
        key_df     : Optional[str] = None,
        key_md5    : Optional[str] = None,

    ) -> None :
    """
    Initialize required session_state keys.
    """
    key_df  = KEY_DF  if key_df  is None else key_df
    key_md5 = KEY_MD5 if key_md5 is None else key_md5
    # NOTE: KEY_EDITOR is intentionally NOT touched here.
    # Streamlit owns the session_state entry for any key used by a widget –
    # writing to it manually raises StreamlitValueAssignmentNotAllowedError.

    if key_df not in st.session_state :
        st.session_state[key_df] = pl.DataFrame()

    if key_md5 not in st.session_state :
        st.session_state[key_md5] = None

    if KEY_VALIDATED not in st.session_state :
        st.session_state[KEY_VALIDATED] = False

    if KEY_FILE not in st.session_state :
        st.session_state[KEY_FILE] = None

    if dataframe is None :

        if date is None or filename is None :
            return None

        df_current = st.session_state.get(key_df)

        if isinstance(df_current, pl.DataFrame) and not df_current.is_empty() :
            return None

        dataframe, md5, _ = read_trade_recap_by_date(date, filename)

    if dataframe is not None :
        st.session_state[key_df] = dataframe

    st.session_state[key_md5] = md5

    return None


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def trades () -> None :
    """
    Main entry.
    """
    filename, date = date_history_section()

    if filename is None or date is None :
        return None

    st.divider()

    # ── Flush state when file changes ────────────────────────────────────────
    if st.session_state.get(KEY_FILE) != filename :
        for k in (KEY_DF, KEY_DF_BASE, KEY_MD5, KEY_VALIDATED) :
            st.session_state.pop(k, None)
        st.session_state[KEY_EDITOR_GEN] = st.session_state.get(KEY_EDITOR_GEN, 0) + 1
        st.session_state[KEY_FILE] = filename

    # ── Load + prepare (once per file, never overwrites user edits) ──────────
    # Do NOT call read_trade_recap_by_date on every rerun – that would
    # overwrite KEY_DF with the raw file and destroy user label changes.
    # Only load when KEY_DF is absent or empty (first visit after a file change).
    df_current = st.session_state.get(KEY_DF)
    df_missing = not isinstance(df_current, pl.DataFrame) or df_current.is_empty()

    if df_missing :
        dataframe, md5, _ = read_trade_recap_by_date(date, filename)
        ensure_session_keys(dataframe, md5, date, filename)

    dataframe = st.session_state[KEY_DF]
    md5       = st.session_state[KEY_MD5]

    # prepare only runs when Label col is missing (i.e. first load)
    if "Label" not in dataframe.columns :
        dataframe, md5 = prepare_master_trade_recap_section(dataframe, md5, date, filename)
        st.session_state[KEY_DF]  = dataframe
        st.session_state[KEY_MD5] = md5

    # KEY_DF_BASE is the immutable pandas snapshot used as data= in the editor.
    # Set it once on first load and never touch it again during editing.
    if st.session_state.get(KEY_DF_BASE) is None :
        st.session_state[KEY_DF_BASE] = st.session_state[KEY_DF].to_pandas()

    # ── Render ────────────────────────────────────────────────────────────────
    edit_master_trade_recap_section(date, filename)

    return None


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def date_history_section (format : Optional[str] = "%Y_%m_%d") -> Tuple[Optional[str], Optional[str | dt.datetime | dt.date]] :
    """
    Date picker + Run button.
    """
    date = st.date_input("Choose a date")

    if st.button("Run Trade Recap") :
        trade_recap_launcher(date)

    filename, real_date = find_most_recent_file_by_date(date)

    date      = str_to_date(date)
    real_date = str_to_date(real_date, format)

    if date != real_date :
        st.warning("[-] No trade Recap generated for the selected Date")
        return None, None

    st.warning(f"[+] Trade recap already generated for the selected date: {filename}")
    
    return filename, real_date


def prepare_master_trade_recap_section (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5       : Optional[str]           = None,
        date      : Optional[str | dt.datetime | dt.date] = None,
        filename  : Optional[str] = None,
    
    ) -> Tuple[pl.DataFrame, Optional[str]] :
    """
    Add Label column if missing and apply automatic OTC/FX logic.
    """
    dataframe, md5, _ = read_trade_recap_by_date(date, filename) if dataframe is None else (dataframe, md5, date)

    if dataframe is None or dataframe.is_empty() :
        return pl.DataFrame(), md5

    if "Label" not in dataframe.columns :
        dataframe = dataframe.with_columns(pl.lit("").alias("Label"))

    dataframe = dataframe.with_columns(
        pl.col("Label").fill_null("").cast(pl.Utf8)
    ).select(["Label"] + [c for c in dataframe.columns if c != "Label"])

    dataframe, md5 = apply_otc_fx_logic_to_trade(dataframe)

    return dataframe, md5


def edit_master_trade_recap_section (
        
        date     : Optional[str | dt.datetime | dt.date] = None,
        filename : Optional[str] = None,
        
    ) -> None :
    """
    Editor + validation + exports.
    """
    ensure_session_keys(date=date, filename=filename)

    center_h5("Trade Recap Editor")
    st.write("")

    base_pd : Optional[pd.DataFrame] = st.session_state.get(KEY_DF_BASE)

    if base_pd is None or base_pd.empty :
        st.info("No table loaded yet.")
        return None

    is_validated : bool = st.session_state.get(KEY_VALIDATED, False)

    # ── Pre-validation: interactive editor ───────────────────────────────────
    # data= is always KEY_DF_BASE – the stable, never-mutated original.
    # Streamlit accumulates diffs on top of it internally, so edited_pd always
    # reflects base + every change the user has made, with no double-apply bug.
    if not is_validated :

        edited_pd = st.data_editor(

            base_pd,
            key                 = _editor_widget_key(),
            use_container_width = True,
            num_rows            = "dynamic",

            column_config = {
                "Label" : st.column_config.SelectboxColumn(
                    "Label",
                    options = ["OTC", "FX", "LISTED"],
                ),
            },

        )

        st.write("")

        if st.button("✅ Validate Trade Recap", use_container_width=True) :
            st.session_state[KEY_DF] = pl.from_pandas(edited_pd).with_columns(
                pl.col("Label").fill_null("").cast(pl.Utf8)
            )
            st.session_state[KEY_VALIDATED] = True
            st.rerun()

        return None

    # ── Post-validation: show frozen result + exports ─────────────────────────
    export_df = st.session_state.get(KEY_DF, pl.DataFrame())
    date_str  = str(date).replace("-", "_") if date is not None else "DATE"

    st.success("✅ Trade Recap validated.")

    # Show the frozen validated dataframe so the user can see their changes
    st.dataframe(export_df, use_container_width=True)

    st.write("")

    if st.button("🔓 Reset & Edit Again", use_container_width=True) :
        # Go back to the original pre-edit base (not the validated state)
        st.session_state[KEY_VALIDATED]  = False
        st.session_state[KEY_EDITOR_GEN] = st.session_state.get(KEY_EDITOR_GEN, 0) + 1
        st.rerun()

    st.write("")

    # ── Master exports ────────────────────────────────────────────────────────
    center_h5("Master Exports")
    st.write("")

    col_left, col_right = st.columns(2)

    with col_left :
        st.download_button(
            label               = "⬇️ Download Master Excel",
            data                = polars_to_excel_bytes(export_df, sheet_name="MASTER"),
            file_name           = f"MASTER_{date_str}.xlsx",
            mime                = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width = True,
        )

    with col_right :
        st.download_button(
            label               = "📧 Download Master Email Draft",
            data                = generate_email_draft_bytes(export_df, label="MASTER", date=date),
            file_name           = f"EMAIL_MASTER_{date_str}.txt",
            mime                = "text/plain",
            use_container_width = True,
        )

    st.divider()

    # ── Split FX / OTC ────────────────────────────────────────────────────────
    split_fx_otc_section(export_df, date=date)

    return None


def split_fx_otc_section (dataframe : pl.DataFrame, date : Optional[str | dt.datetime | dt.date] = None) -> None :
    """
    Side-by-side FX / OTC viewer with per-table exports.
    """
    if dataframe is None or dataframe.is_empty() :
        return None
    
    col1, col2 = st.columns(2)

    with col1 :
        fx_recap_section(dataframe, date=date)

    with col2 :
        otc_recap_section(dataframe, date=date)

    return None


def fx_recap_section (dataframe : Optional[pl.DataFrame] = None, date : Optional[str | dt.datetime | dt.date] = None) -> None :
    """
    FX trades viewer + exports.
    """
    center_h5("FX Trade Recap")
    st.write("")

    if dataframe is None or dataframe.is_empty() :
        st.info("No data available.")
        return None

    date_str = str(date).replace("-", "_") if date is not None else "DATE"
    fx_df    = dataframe.filter(pl.col("Label") == "FX")

    if fx_df.is_empty() :
        st.info("No FX trades for this date.")
        _download_empty_email("FX", date)
        return None

    st.dataframe(fx_df, use_container_width=True)
    st.write("")

    col_left, col_right = st.columns(2)

    with col_left :
        st.download_button(
            label               = "⬇️ Download FX Excel",
            data                = polars_to_excel_bytes(fx_df, sheet_name="FX"),
            file_name           = f"FX_{date_str}.xlsx",
            mime                = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width = True,
        )

    with col_right :
        st.download_button(
            label               = "📧 Download FX Email Draft",
            data                = generate_email_draft_bytes(fx_df, label="FX", date=date),
            file_name           = f"EMAIL_FX_{date_str}.txt",
            mime                = "text/plain",
            use_container_width = True,
        )

    return None


def otc_recap_section (dataframe : Optional[pl.DataFrame] = None, date : Optional[str | dt.datetime | dt.date] = None) -> None :
    """
    OTC trades viewer + exports.
    """
    center_h5("OTC Trade Recap")
    st.write("")

    if dataframe is None or dataframe.is_empty() :
        st.info("No data available.")
        return None

    date_str = str(date).replace("-", "_") if date is not None else "DATE"
    otc_df   = dataframe.filter(pl.col("Label") == "OTC")

    if otc_df.is_empty() :
        st.info("No OTC trades for this date.")
        _download_empty_email("OTC", date)
        return None

    st.dataframe(otc_df, use_container_width=True)
    st.write("")

    col_left, col_right = st.columns(2)

    with col_left :
        st.download_button(
            label               = "⬇️ Download OTC Excel",
            data                = polars_to_excel_bytes(otc_df, sheet_name="OTC"),
            file_name           = f"OTC_{date_str}.xlsx",
            mime                = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width = True,
        )

    with col_right :
        st.download_button(
            label               = "📧 Download OTC Email Draft",
            data                = generate_email_draft_bytes(otc_df, label="OTC", date=date),
            file_name           = f"EMAIL_OTC_{date_str}.txt",
            mime                = "text/plain",
            use_container_width = True,
        )

    return None


def _download_empty_email (label : str, date : Optional[str | dt.datetime | dt.date] = None) -> None :
    """
    Offer a 'no trades' email draft when a sub-table is empty.
    """
    date_str = str(date) if date is not None else "N/A"

    body = (
        f"Subject: Trade Recap – {label} – {date_str}\n\n"
        f"Dear Team,\n\n"
        f"No {label} trades to report for {date_str}.\n\n"
        f"Best regards,\nTrade Operations"
    ).encode("utf-8")

    st.download_button(
        label               = f"📧 Download {label} Email (No Trades)",
        data                = body,
        file_name           = f"EMAIL_{label}_{date_str.replace('-','_')}_NO_TRADES.txt",
        mime                = "text/plain",
        use_container_width = True,
    )

    return None


# ---------------------------------------------------------------------------
# Legacy / utility
# ---------------------------------------------------------------------------

def edit_and_export_table (dataframe : Optional[pl.DataFrame] = None, cache_key: str = "edited_data") -> None :
    """
    Generic standalone edit + export helper.
    """
    if dataframe is None or dataframe.is_empty() :
        st.warning("No data available to edit.")
        return None

    dataframe = dataframe.to_pandas()
    edited_df = st.data_editor(dataframe, key=cache_key, use_container_width=True)

    st.write("Edited Table:")
    st.dataframe(edited_df, use_container_width=True)

    if st.button("Export Edited Table") :
        export_df_to_excel(edited_df)


def export_df_to_excel (dataframe : Optional[pd.DataFrame] = None, md5 : Optional[str] = None) -> None :
    """
    Export a pandas DataFrame to Excel via st.download_button.
    """
    polars_df   = pl.from_pandas(dataframe)
    excel_bytes = polars_to_excel_bytes(polars_df)

    st.download_button(
        "⬇️ Download Edited Table (xlsx)",
        data                = excel_bytes,
        file_name           = "edited_table.xlsx",
        mime                = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width = True,
    )