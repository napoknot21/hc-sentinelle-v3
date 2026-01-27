from __future__ import annotations

import polars as pl
import pandas as pd
import datetime as dt
import streamlit as st

from typing import Optional, Tuple, List

from src.utils.formatters import str_to_date
from src.ui.components.text import center_h5
from src.core.api.recap import trade_recap_launcher
from src.core.data.recap import (
    read_trade_recap_by_date,
    find_most_recent_file_by_date,
    clean_structure_from_dataframe,
    apply_user_review_defaults,
    apply_otc_fx_logic_to_trade
)


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


def date_history_section(
    format: Optional[str] = "%Y_%m_%d",
) -> Tuple[Optional[str], Optional[str | dt.datetime | dt.date]]:
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


def edit_master_trade_recap_section(
    date: Optional[str | dt.datetime | dt.date] = None,
    filename: Optional[str] = None,
    view: Optional[bool] = True,
) -> None:
    """
    Editor + preset label in a single st.form (stable / no flicker).
    """

    view = view_selector_section()
    meta = (str(date), str(filename), bool(view))

    # Load once per (date, filename, view)
    if st.session_state.get("trade_recap_meta") != meta :
        
        st.session_state["trade_recap_meta"] = meta
        st.session_state["trade_recap_df"] = prepare_master_trade_recap_section(date, filename, view)

        # reset editor widget state on reload
        st.session_state.pop("trade_recap_editor", None)
        st.session_state.pop("trade_recap_label_choice", None)

    df = st.session_state.get("trade_recap_df")
    if df is None or df.is_empty():
        st.info("No table loaded yet.")
        return None

    with st.form("recap_form", clear_on_submit=False):

        left, right = st.columns([3, 1], vertical_alignment="top")

        with left :

            edited = st.data_editor(
                df,
                key="trade_recap_editor",
                column_config={"Select": st.column_config.CheckboxColumn("Select")},
            )

        with right :

            center_h5("Labelisation (OTC / FX)")
            st.caption("Optionnel : preset rapide pour classer en bulk.")

            label_choice = st.selectbox(
                "Set label to",
                ["OTC", "FX", "OTHER", "UNASSIGNED"],
                key="trade_recap_label_choice",
            )

            submitted = st.form_submit_button("✅ Apply", use_container_width=True)
            
            if submitted :
                st.rerun()

    if submitted:
        # keep polars stable
        if isinstance(edited, pd.DataFrame):
            edited = pl.from_pandas(edited)

        # Apply preset to selected rows only
        edited = edited.with_columns(
            pl.when(pl.col("Select") == True)
            .then(pl.lit(label_choice))
            .otherwise(pl.col("Label"))
            .alias("Label")
        )

        # Optional: reset Select after apply
        # edited = edited.with_columns(pl.lit(False).alias("Select"))

        st.session_state["trade_recap_df"] = edited
        st.success("Applied (Label set on selected rows).")

    
    if st.button("Validate Master Recap") :

        
        st.write("Good")

    return None


def prepare_master_trade_recap_section(
    date: Optional[str | dt.datetime | dt.date] = None,
    filename: Optional[str] = None,
    view: Optional[bool] = True,
) -> pl.DataFrame:
    dataframe, md5, _ = read_trade_recap_by_date(date, filename, light=view)

    # dataframe = clean_structure_from_dataframe(dataframe, md5)
    # dataframe = apply_user_review_defaults(dataframe)

    if "Select" not in dataframe.columns:
        dataframe = dataframe.with_columns(pl.lit(False).alias("Select"))

    if "Label" not in dataframe.columns:
        dataframe = dataframe.with_columns(pl.lit("").alias("Label"))

    dataframe = (
        dataframe.with_columns(
            [
                pl.col("Select").fill_null(False).cast(pl.Boolean),
                pl.col("Label").fill_null("").cast(pl.Utf8),
            ]
        )
        .select(["Select", "Label"] + [c for c in dataframe.columns if c not in ("Select", "Label")])
    )

    st.write(dataframe.columns)
    dataframe = apply_otc_fx_logic_to_trade(dataframe)

    return dataframe


def view_selector_section(
        
        views: Optional[List[str]] = None,
        label_view: Optional[str] = None,
        key_view: Optional[str] = None,
    ) -> bool :
    """
    Docstring for view_selector_section
    
    :param views: Description
    :type views: Optional[List[str]]
    :param label_view: Description
    :type label_view: Optional[str]
    :param key_view: Description
    :type key_view: Optional[str]
    :return: Description
    :rtype: bool
    """
    views = ["Light", "Complete"] if views is None else views
    label_view = "Select a view" if label_view is None else label_view

    key_view = "Recaps_Trades_view_selector" if key_view is None else key_view

    view = st.selectbox(label_view, views, key=key_view)

    return view == views[0]
