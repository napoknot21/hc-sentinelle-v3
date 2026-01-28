from __future__ import annotations

import datetime as dt
from typing import Optional, Tuple, List

import polars as pl
import pandas as pd
import streamlit as st

from src.utils.formatters import str_to_date
from src.ui.components.text import center_h5
from src.core.api.recap import trade_recap_launcher
from src.core.data.recap import (
    read_trade_recap_by_date,
    find_most_recent_file_by_date,
    clean_structure_from_dataframe,
    apply_user_review_defaults,
    apply_otc_fx_logic_to_trade,
)

# ============================================================
# Helpers
# ============================================================

def split_master_recap_otc_fx(
    df: pl.DataFrame,
    label_col: str = "Label",
    drop_cols: Optional[List[str]] = None,
) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """
    Split df into OTC and FX based on Label, and drop helper cols.
    Other labels are ignored.
    """
    if drop_cols is None:
        drop_cols = ["Select", "Label"]

    if df is None or df.is_empty():
        return pl.DataFrame(), pl.DataFrame()

    if label_col not in df.columns:
        raise ValueError(f"Missing column: {label_col}")

    df_otc = df.filter(pl.col(label_col) == "OTC")
    df_fx = df.filter(pl.col(label_col) == "FX")

    for c in drop_cols:
        if c in df_otc.columns:
            df_otc = df_otc.drop(c)
        if c in df_fx.columns:
            df_fx = df_fx.drop(c)

    return df_otc, df_fx


def drop_temp_cols_master(df: pl.DataFrame, drop_cols: Optional[List[str]] = None) -> pl.DataFrame:
    """
    Drop temp columns from master after validation (Select, Label).
    """
    if df is None or df.is_empty():
        return pl.DataFrame()

    drop_cols = ["Select", "Label"] if drop_cols is None else drop_cols
    existing = [c for c in drop_cols if c in df.columns]
    return df.drop(existing) if existing else df


def polars_to_excel_bytes(df: pl.DataFrame, sheet_name: str = "Data") -> bytes:
    """
    Convert a Polars DataFrame to an Excel file in-memory.
    Replace this with your formatting/export script later if needed.
    """
    import io

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_pandas().to_excel(writer, sheet_name=sheet_name, index=False)
    out.seek(0)
    return out.read()


def _build_row_key_expr(cols: List[str]) -> pl.Expr:
    return pl.concat_str([pl.col(c).fill_null("").cast(pl.Utf8) for c in cols], separator="|")


def apply_labels_from_light_to_complete(
    df_light: pl.DataFrame,
    df_complete: pl.DataFrame,
    label_col: str = "Label",
    select_col: str = "Select",
) -> pl.DataFrame:
    """
    Transfer (Label, Select) from df_light to df_complete using a key built from shared columns.
    Best-effort: if there are duplicates on the key, keep last.
    """
    if df_light is None or df_light.is_empty():
        return df_complete
    if df_complete is None or df_complete.is_empty():
        return df_complete

    common = [c for c in df_light.columns if c in df_complete.columns and c not in (label_col, select_col)]
    if not common:
        # fallback: align by row order (risky)
        n = min(df_light.height, df_complete.height)
        light_slice = df_light.head(n).select([label_col, select_col])
        comp_slice = df_complete.head(n).with_columns(
            [
                light_slice.get_column(label_col).alias(label_col),
                light_slice.get_column(select_col).alias(select_col),
            ]
        )
        return pl.concat([comp_slice, df_complete.slice(n, df_complete.height - n)], how="vertical")

    k_expr = _build_row_key_expr(common)

    light_map = (
        df_light
        .with_columns(k_expr.alias("__k"))
        .select(["__k", label_col, select_col])
        .unique(subset=["__k"], keep="last")
    )

    out = (
        df_complete
        .with_columns(k_expr.alias("__k"))
        .join(light_map, on="__k", how="left", suffix="_map")
        .with_columns(
            [
                pl.coalesce([pl.col(f"{label_col}_map"), pl.col(label_col)]).alias(label_col),
                pl.coalesce([pl.col(f"{select_col}_map"), pl.col(select_col)]).alias(select_col),
            ]
        )
        .drop(["__k", f"{label_col}_map", f"{select_col}_map"])
    )
    return out


# ============================================================
# Main entry
# ============================================================

def trades() -> None:
    """
    Main entry
    """
    filename, date = date_history_section()

    if filename is None or date is None:
        return None

    st.divider()

    edit_master_trade_recap_section(date, filename)

    return None


def date_history_section(format: Optional[str] = "%Y_%m_%d") -> Tuple[Optional[str], Optional[str | dt.datetime | dt.date]]:
    date = st.date_input("Choose a date")

    if st.button("Run Trade Recap"):
        trade_recap_launcher(date)

    filename, real_date = find_most_recent_file_by_date(date)

    date = str_to_date(date)
    real_date = str_to_date(real_date, format)

    if date != real_date:
        st.warning("No trade Recap generated for the selected Date")
        return None, None

    st.warning(f"Trade recap already generated for the selected date: {filename}")
    return filename, real_date


# ============================================================
# UI + Logic
# ============================================================

def edit_master_trade_recap_section(
    date: Optional[str | dt.datetime | dt.date] = None,
    filename: Optional[str] = None,
    view: Optional[bool] = True,
) -> None:
    """
    - Edit mode: user can edit Select + Label.
    - Validate mode: freeze master (drop Select/Label), split OTC/FX.
      Display: light.
      Export/email: complete (all columns).
    """

    view = view_selector_section()  # True => Light, False => Complete

    meta = (str(date), str(filename))
    validated_key = f"trade_recap_validated::{meta[0]}::{meta[1]}"

    # reset state when date/filename changes
    if st.session_state.get("trade_recap_meta") != meta:
        st.session_state["trade_recap_meta"] = meta

        st.session_state.pop("trade_recap_df_light", None)
        st.session_state.pop("trade_recap_df_complete", None)

        st.session_state.pop(validated_key, None)

        # display (light)
        st.session_state.pop("trade_recap_master_frozen", None)
        st.session_state.pop("trade_recap_split_otc", None)
        st.session_state.pop("trade_recap_split_fx", None)

        # export/email (complete)
        st.session_state.pop("trade_recap_export_master", None)
        st.session_state.pop("trade_recap_export_otc", None)
        st.session_state.pop("trade_recap_export_fx", None)

        # reset widget state
        st.session_state.pop("trade_recap_editor_light", None)
        st.session_state.pop("trade_recap_editor_complete", None)
        st.session_state.pop("trade_recap_label_choice_light", None)
        st.session_state.pop("trade_recap_label_choice_complete", None)

    # load the chosen view into cache
    cache_key = "trade_recap_df_light" if view else "trade_recap_df_complete"
    if st.session_state.get(cache_key) is None:
        st.session_state[cache_key] = prepare_master_trade_recap_section(date, filename, view)

    df = st.session_state.get(cache_key)
    if df is None or df.is_empty():
        st.info("No table loaded yet.")
        return None

    is_validated = bool(st.session_state.get(validated_key, False))

    # ============================================================
    # ✅ FROZEN MODE
    # ============================================================
    if is_validated:
        st.success("✅ Master recap validated — frozen.")

        # display (light)
        master_frozen_light = st.session_state.get("trade_recap_master_frozen", pl.DataFrame())
        otc_light = st.session_state.get("trade_recap_split_otc", pl.DataFrame())
        fx_light = st.session_state.get("trade_recap_split_fx", pl.DataFrame())

        # export/email (complete)
        master_export = st.session_state.get("trade_recap_export_master", pl.DataFrame())
        otc_export = st.session_state.get("trade_recap_export_otc", pl.DataFrame())
        fx_export = st.session_state.get("trade_recap_export_fx", pl.DataFrame())

        # ---- MASTER (display light, actions use complete)
        st.subheader("Master Trade Recap (frozen)")
        st.dataframe(master_frozen_light, use_container_width=True)

        cM1, cM2 = st.columns(2)
        with cM1:
            if st.button("📧 Generate MASTER email", use_container_width=True, key="btn_email_master"):
                # TODO: call your email generation script using master_export (COMPLETE)
                st.info("Hook: call your email generation script for MASTER (complete) here.")

        with cM2:
            master_bytes = polars_to_excel_bytes(master_export, sheet_name="MASTER")
            st.download_button(
                "⬇️ Download MASTER (xlsx)",
                data=master_bytes,
                file_name=f"MASTER_{meta[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_master",
            )

        # ---- OTC (display light, actions use complete)
        st.subheader("OTC trades (light display / complete export)")
        st.dataframe(otc_light, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📧 Generate OTC email", use_container_width=True, key="btn_email_otc"):
                # TODO: call your email generation script using otc_export (COMPLETE)
                st.info("Hook: call your email generation script for OTC (complete) here.")

        with c2:
            otc_bytes = polars_to_excel_bytes(otc_export, sheet_name="OTC")
            st.download_button(
                "⬇️ Download OTC (xlsx)",
                data=otc_bytes,
                file_name=f"OTC_{meta[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_otc",
            )

        # ---- FX (display light, actions use complete)
        st.subheader("FX trades (light display / complete export)")
        st.dataframe(fx_light, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            if st.button("📧 Generate FX email", use_container_width=True, key="btn_email_fx"):
                # TODO: call your email generation script using fx_export (COMPLETE)
                st.info("Hook: call your email generation script for FX (complete) here.")

        with c4:
            fx_bytes = polars_to_excel_bytes(fx_export, sheet_name="FX")
            st.download_button(
                "⬇️ Download FX (xlsx)",
                data=fx_bytes,
                file_name=f"FX_{meta[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_fx",
            )

        return None

    # ============================================================
    # ✏️ EDIT MODE
    # ============================================================

    editor_key = "trade_recap_editor_light" if view else "trade_recap_editor_complete"
    label_key = "trade_recap_label_choice_light" if view else "trade_recap_label_choice_complete"

    with st.form("recap_form", clear_on_submit=False):
        left, right = st.columns([3, 1], vertical_alignment="top")

        with left:
            edited = st.data_editor(
                df,
                key=editor_key,
                column_config={"Select": st.column_config.CheckboxColumn("Select")},
                use_container_width=True,
            )

        with right:
            center_h5("Labelisation (OTC / FX)")
            st.caption("Optionnel : preset rapide pour classer en bulk.")

            label_choice = st.selectbox(
                "Set label to",
                ["OTC", "FX", "OTHER"],
                key=label_key,
            )

            apply_clicked = st.form_submit_button("✅ Apply", use_container_width=True)

    if apply_clicked:
        if isinstance(edited, pd.DataFrame):
            edited = pl.from_pandas(edited)

        edited = edited.with_columns(
            pl.when(pl.col("Select") == True)
            .then(pl.lit(label_choice))
            .otherwise(pl.col("Label"))
            .alias("Label")
        )

        st.session_state[cache_key] = edited
        st.success("Applied (Label set on selected rows).")
        st.rerun()

    # ✅ Validate button
    if st.button("Validate Master Recap", type="primary"):

        df_current = st.session_state.get(cache_key)
        if df_current is None or df_current.is_empty():
            st.warning("Nothing to validate.")
            return None

        # ALWAYS load complete for export/email
        if st.session_state.get("trade_recap_df_complete") is None:
            st.session_state["trade_recap_df_complete"] = prepare_master_trade_recap_section(date, filename, view=False)

        df_complete = st.session_state.get("trade_recap_df_complete")
        if df_complete is None or df_complete.is_empty():
            st.warning("Complete view is empty — cannot export.")
            return None

        # Transfer Label/Select edits from current view -> complete view
        df_complete_labeled = apply_labels_from_light_to_complete(df_current, df_complete)

        # DISPLAY (light): split + drop temp cols everywhere
        otc_light, fx_light = split_master_recap_otc_fx(df_current, drop_cols=["Select", "Label"])
        master_frozen_light = drop_temp_cols_master(df_current, drop_cols=["Select", "Label"])

        # EXPORT/EMAIL (complete): split + drop temp cols everywhere
        otc_export, fx_export = split_master_recap_otc_fx(df_complete_labeled, drop_cols=["Select", "Label"])
        master_export = drop_temp_cols_master(df_complete_labeled, drop_cols=["Select", "Label"])

        # store display (light)
        st.session_state["trade_recap_master_frozen"] = master_frozen_light
        st.session_state["trade_recap_split_otc"] = otc_light
        st.session_state["trade_recap_split_fx"] = fx_light

        # store export/email (complete)
        st.session_state["trade_recap_export_master"] = master_export
        st.session_state["trade_recap_export_otc"] = otc_export
        st.session_state["trade_recap_export_fx"] = fx_export

        st.session_state[validated_key] = True
        st.success("Master recap validated. Display=light, Export/Email=complete.")
        st.rerun()

    return None


def prepare_master_trade_recap_section(
    date: Optional[str | dt.datetime | dt.date] = None,
    filename: Optional[str] = None,
    view: Optional[bool] = True,
) -> pl.DataFrame:
    dataframe, md5, _ = read_trade_recap_by_date(date, filename, light=view)

    if dataframe is None or dataframe.is_empty():
        return pl.DataFrame()

    # dataframe = clean_structure_from_dataframe(dataframe, md5)
    # dataframe = apply_user_review_defaults(dataframe)

    if "Select" not in dataframe.columns:
        dataframe = dataframe.with_columns(pl.lit(False).alias("Select"))

    if "Label" not in dataframe.columns:
        dataframe = dataframe.with_columns(pl.lit("").alias("Label"))

    dataframe = dataframe.with_columns(
        [
            pl.col("Select").fill_null(False).cast(pl.Boolean),
            pl.col("Label").fill_null("").cast(pl.Utf8),
        ]
    ).select(["Select", "Label"] + [c for c in dataframe.columns if c not in ("Select", "Label")])

    dataframe = apply_otc_fx_logic_to_trade(dataframe)
    return dataframe


def view_selector_section(
    views: Optional[List[str]] = None,
    label_view: Optional[str] = None,
    key_view: Optional[str] = None,
) -> bool:
    """
    View selector (Light vs Complete)
    """
    views = ["Light", "Complete"] if views is None else views
    label_view = "Select a view" if label_view is None else label_view
    key_view = "Recaps_Trades_view_selector" if key_view is None else key_view

    v = st.selectbox(label_view, views, key=key_view)
    return v == views[0]
