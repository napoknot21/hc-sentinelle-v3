from __future__ import annotations

import os
import re
import datetime as dt
from typing import Dict, List, Optional, Tuple

import polars as pl
import streamlit as st

from src.config.parameters import (
    TRADE_RECAP_EMAIL_COLUMNS,
    TRADE_RECAP_MIN_COLUMNS,
    TRADE_RECAP_RAW_FILE_REGEX,
)
from src.config.paths import TREADE_RECAP_DATA_RAW_DIR_ABS_PATH
from src.core.data.recap import (
    apply_email_recap_columns,
    apply_otc_fx_logic_to_trade,
    clean_structure_from_dataframe,
)
from src.ui.components.text import center_h5
from src.utils.data_io import load_excel_to_dataframe, polars_to_excel_bytes
from src.utils.dates import monday_of_week, parse_date_any, parse_datetime_any


SOURCE_DATE_COL = "Recap Date"
SOURCE_FILE_COL = "Source File"
SOURCE_AS_OF_COL = "As Of"

SOURCE_COLUMNS = {
    SOURCE_DATE_COL: pl.Date,
    SOURCE_AS_OF_COL: pl.Datetime,
    SOURCE_FILE_COL: pl.Utf8,
}

DISPLAY_SOURCE_COLUMNS = [SOURCE_DATE_COL, SOURCE_AS_OF_COL, SOURCE_FILE_COL]


def viewer () -> None :
    """
    Weekly historical trade recap viewer.
    """
    render_viewer_header()
    render_weekly_viewer()

    return None


def render_viewer_header () -> None :
    """
    Render the page header.
    """
    center_h5("Trade Recap Weekly Viewer")
    st.write("")


def render_weekly_viewer () -> None :
    """
    Render the selected weekly recap view.
    """
    monday = select_week_monday()
    week_files = find_week_trade_recap_files(monday)

    if not week_files :
        st.warning("No generated trade recap Excel file found for this week.")
        return None

    render_week_files_metadata(week_files)
    data_viewer(load_week_trade_recaps_with_spinner(week_files), monday)

    return None


def select_week_monday () -> dt.date :
    """
    Select a week using its Monday.
    """
    today = dt.date.today()
    default_monday = monday_of_week(today)

    selected = st.date_input(
        "Select week Monday",
        value=default_monday,
        help="The viewer loads the latest generated Excel file for each day from Monday to Friday.",
    )

    monday = monday_of_week(selected)

    if selected != monday :
        st.info(f"Selected date adjusted to week Monday: {monday:%Y-%m-%d}")

    friday = monday + dt.timedelta(days=4)
    st.caption(f"Week loaded: {monday:%Y-%m-%d} to {friday:%Y-%m-%d}")

    return monday


def render_week_files_metadata (week_files : List[Tuple[dt.date, dt.datetime, str]]) -> None :
    """
    Render the list of files selected for the week.
    """
    st.caption("Files loaded from the historical recap directory only. No API call is made.")
    st.dataframe(
        build_week_files_metadata_dataframe(week_files),
        use_container_width=True,
        hide_index=True,
    )

    return None


def build_week_files_metadata_dataframe (week_files : List[Tuple[dt.date, dt.datetime, str]]) -> pl.DataFrame :
    """
    Build the metadata dataframe displayed above the recap data.
    """
    return pl.DataFrame(
        [
            {
                "Date" : trade_date,
                "As Of" : as_of,
                "File" : filename,
            }
            for trade_date, as_of, filename in week_files
        ]
    )


def load_week_trade_recaps_with_spinner (week_files : List[Tuple[dt.date, dt.datetime, str]]) -> pl.DataFrame :
    """
    Load weekly recap files with Streamlit feedback.
    """
    with st.spinner("Loading and normalizing weekly Excel files...") :
        return load_week_trade_recaps(week_files)


def data_viewer (

        dataframe : Optional[pl.DataFrame] = None,
        monday : Optional[dt.date] = None,

    ) -> None :
    """
    Render the normalized weekly data with simple filters.
    """
    if dataframe is None or dataframe.is_empty() :
        st.info("No trade data available for the selected week.")
        return None

    filtered = weekly_filters(dataframe)
    st.write("")

    render_week_summary_metrics(filtered)

    if filtered.is_empty() :
        st.info("No rows match the selected filters.")
        return None

    st.write("")

    display_df = build_display_dataframe(filtered, compact=select_compact_view_mode())
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    render_week_download_button(display_df, monday)

    return None


def render_week_summary_metrics (dataframe : pl.DataFrame) -> None :
    """
    Render the weekly recap summary metrics.
    """
    col_rows, col_trades, col_legs, col_files = st.columns(4)
    col_rows.metric("Rows", f"{dataframe.height:,}")
    col_trades.metric("Trades", f"{unique_count(dataframe, 'tradeId'):,}")
    col_legs.metric("Legs", f"{unique_count(dataframe, 'tradeLegId'):,}")
    col_files.metric("Files", f"{unique_count(dataframe, SOURCE_FILE_COL):,}")

    return None


def select_compact_view_mode () -> bool :
    """
    Return whether the compact display mode is selected.
    """
    return st.radio(
        "View",
        options=["Compact", "All columns"],
        index=0,
        horizontal=True,
    ) == "Compact"


def render_week_download_button (

        dataframe : pl.DataFrame,
        monday : Optional[dt.date] = None,

    ) -> None :
    """
    Render the weekly Excel download button.
    """

    st.download_button(
        label="Download normalized week Excel",
        data=polars_to_excel_bytes(dataframe, sheet_name="Week"),
        file_name=week_export_filename(monday),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    return None


def find_week_trade_recap_files (

        monday : dt.date,
        dir_abs_path : Optional[str] = None,

    ) -> List[Tuple[dt.date, dt.datetime, str]]:
    """
    Return the latest generated recap file for each weekday in a Monday-Friday week.
    """
    return [
        found
        for day in (monday + dt.timedelta(days=i) for i in range(5))
        if (found := find_latest_trade_recap_file_for_date(day, dir_abs_path)) is not None
    ]


def find_latest_trade_recap_file_for_date (

        date : dt.date,
        dir_abs_path : Optional[str] = None,

    ) -> Optional[Tuple[dt.date, dt.datetime, str]]:
    """
    Find the latest Excel recap matching one trade date.
    """
    dir_abs_path = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path

    if not dir_abs_path or not os.path.isdir(dir_abs_path) :
        return None

    best: Optional[Tuple[dt.datetime, str]] = None

    with os.scandir(dir_abs_path) as it :
        for entry in it :
            if not entry.is_file() or not entry.name.lower().endswith(".xlsx") :
                continue

            parsed = parse_trade_recap_filename(entry.name)

            if parsed is None :
                continue

            trade_date, as_of = parsed

            if trade_date != date :
                continue

            if best is None or as_of > best[0] :
                best = (as_of, entry.name)

    if best is None :
        return None

    return date, best[0], best[1]


def parse_trade_recap_filename (filename : str) -> Optional[Tuple[dt.date, dt.datetime]]:
    """
    Parse trade date and as-of timestamp from a recap filename using the configured regex.
    """
    match = TRADE_RECAP_RAW_FILE_REGEX.match(filename)

    if not match or len(match.groups()) < 2 :
        return None

    trade_date_raw, as_of_raw = match.groups()[:2]
    trade_date = parse_date_any(trade_date_raw)
    as_of = parse_datetime_any(as_of_raw)

    if trade_date is None or as_of is None :
        return None

    return trade_date, as_of


def load_week_trade_recaps (

        week_files : List[Tuple[dt.date, dt.datetime, str]],
        dir_abs_path : Optional[str] = None,

    ) -> pl.DataFrame:
    """
    Load and normalize several daily Excel recaps into one weekly dataframe.
    """
    dir_abs_path = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if dir_abs_path is None else dir_abs_path
    frames: List[pl.DataFrame] = []

    for trade_date, as_of, filename in week_files :
        full_path = os.path.join(dir_abs_path, filename)
        dataframe, _ = load_excel_to_dataframe(
            full_path,
            schema_overrides=TRADE_RECAP_MIN_COLUMNS,
        )

        if dataframe is None or dataframe.is_empty() :
            continue

        frames.append(normalize_trade_recap_dataframe(dataframe, trade_date, as_of, filename))

    if not frames :
        return pl.DataFrame()

    return pl.concat(frames, how="diagonal_relaxed").sort(
        [SOURCE_DATE_COL, SOURCE_AS_OF_COL],
        descending=[False, False],
    )


def normalize_trade_recap_dataframe (

        dataframe : pl.DataFrame,
        trade_date : dt.date,
        as_of : dt.datetime,
        filename : str,

    ) -> pl.DataFrame:
    """
    Normalize one historical recap file so it can be concatenated with other days.
    """
    dataframe = clean_structure_from_dataframe(dataframe)

    if dataframe is None or dataframe.is_empty() :
        return pl.DataFrame()

    dataframe = ensure_columns(dataframe, normal_schema())
    dataframe = dataframe.with_columns(
        [
            pl.lit(trade_date).cast(pl.Date).alias(SOURCE_DATE_COL),
            pl.lit(as_of).cast(pl.Datetime).alias(SOURCE_AS_OF_COL),
            pl.lit(filename).cast(pl.Utf8).alias(SOURCE_FILE_COL),
        ]
    )

    if "Label" not in dataframe.columns :
        dataframe = dataframe.with_columns(pl.lit("").cast(pl.Utf8).alias("Label"))

    dataframe = dataframe.with_columns(pl.col("Label").fill_null("").cast(pl.Utf8))
    dataframe, _ = apply_otc_fx_logic_to_trade(dataframe)

    return dataframe


def normal_schema () -> Dict[str, pl.DataType]:
    """
    Required columns for a stable weekly view.
    """
    schema = {}
    schema.update(SOURCE_COLUMNS)
    schema.update({"Label": pl.Utf8})
    schema.update(TRADE_RECAP_MIN_COLUMNS)
    schema.update(TRADE_RECAP_EMAIL_COLUMNS)

    return schema


def ensure_columns (dataframe : pl.DataFrame, schema : Dict[str, pl.DataType]) -> pl.DataFrame:
    """
    Add missing columns and cast known columns permissively.
    """
    if dataframe is None or dataframe.is_empty() :
        return pl.DataFrame()

    missing = [
        pl.lit(None).cast(dtype).alias(column)
        for column, dtype in schema.items()
        if column not in dataframe.columns
    ]

    if missing :
        dataframe = dataframe.with_columns(missing)

    casts = [
        pl.col(column).cast(dtype, strict=False).alias(column)
        for column, dtype in schema.items()
        if column in dataframe.columns
    ]

    return dataframe.with_columns(casts) if casts else dataframe


def weekly_filters (dataframe : pl.DataFrame) -> pl.DataFrame:
    """
    Apply Streamlit filters to the weekly dataframe.
    """
    with st.expander("Filters", expanded=True) :
        col_1, col_2, col_3, col_4 = st.columns(4)

        with col_1 :
            date_options = sorted(non_null_values(dataframe, SOURCE_DATE_COL))
            selected_dates = st.multiselect("Dates", options=date_options, default=date_options)

        with col_2 :
            label_options = sorted(non_null_values(dataframe, "Label"))
            selected_labels = st.multiselect("Labels", options=label_options, default=label_options)

        with col_3 :
            asset_options = sorted(non_null_values(dataframe, "assetClass"))
            selected_assets = st.multiselect("Asset classes", options=asset_options, default=asset_options)

        with col_4 :
            book_options = sorted(non_null_values(dataframe, "bookName"))
            selected_books = st.multiselect("Books", options=book_options, default=book_options)

        search = st.text_input("Search trade id / code / name / description")

    filtered = dataframe
    filtered = filter_in(filtered, SOURCE_DATE_COL, selected_dates)
    filtered = filter_in(filtered, "Label", selected_labels)
    filtered = filter_in(filtered, "assetClass", selected_assets)
    filtered = filter_in(filtered, "bookName", selected_books)
    filtered = filter_search(filtered, search)

    return filtered


def non_null_values (dataframe : pl.DataFrame, column : str) -> List:
    """
    Return display-safe unique values for a column.
    """
    if column not in dataframe.columns :
        return []

    return dataframe.get_column(column).drop_nulls().unique().to_list()


def filter_in (dataframe : pl.DataFrame, column : str, values : List) -> pl.DataFrame:
    """
    Filter on a list of selected values.
    """
    if not values or column not in dataframe.columns :
        return dataframe

    return dataframe.filter(pl.col(column).is_in(values))


def filter_search (dataframe : pl.DataFrame, search : Optional[str]) -> pl.DataFrame:
    """
    Case-insensitive search over common trade identity columns.
    """
    if search is None or search.strip() == "" :
        return dataframe

    search = re.escape(search.strip().lower())
    searchable_cols = [
        column
        for column in ("tradeId", "tradeLegId", "tradeLegCode", "tradeName", "tradeDescription", "counterparty")
        if column in dataframe.columns
    ]

    if not searchable_cols :
        return dataframe

    conditions = [
        pl.col(column)
        .cast(pl.Utf8, strict=False)
        .fill_null("")
        .str.to_lowercase()
        .str.contains(search)
        for column in searchable_cols
    ]

    condition = conditions[0]

    for item in conditions[1:] :
        condition = condition | item

    return dataframe.filter(condition)


def build_display_dataframe (dataframe : pl.DataFrame, compact : bool = True) -> pl.DataFrame:
    """
    Build either a compact recap view or the full normalized dataframe.
    """
    if not compact :
        return dataframe.select(DISPLAY_SOURCE_COLUMNS + [c for c in dataframe.columns if c not in DISPLAY_SOURCE_COLUMNS])

    compact_df = apply_email_recap_columns(
        dataframe,
        columns_order=TRADE_RECAP_EMAIL_COLUMNS,
        keep_only_defined=True,
    )
    source_df = dataframe.select(DISPLAY_SOURCE_COLUMNS)

    return pl.concat([source_df, compact_df], how="horizontal")


def unique_count (dataframe : pl.DataFrame, column : str) -> int:
    """
    Count unique non-null values in a dataframe column.
    """
    if dataframe is None or dataframe.is_empty() or column not in dataframe.columns :
        return 0

    return dataframe.get_column(column).drop_nulls().n_unique()


def week_export_filename (monday : Optional[dt.date]) -> str:
    """
    Generate a weekly export filename.
    """
    if monday is None :
        monday = monday_of_week()

    friday = monday + dt.timedelta(days=4)

    return f"trade_recap_week_{monday:%Y_%m_%d}_to_{friday:%Y_%m_%d}.xlsx"
