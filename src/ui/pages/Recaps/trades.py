from __future__ import annotations

import io
import datetime as dt
import polars as pl
import streamlit as st

from typing import Any, Dict, Optional, Tuple, List

from src.core.api.recap import trade_recap_launcher
from src.core.data.recap import (
    read_trade_recap_by_date, find_most_recent_file_by_date,
    pick_default_columns
)
from src.utils.formatters import date_to_str, str_to_date

def trades () :
    """
    Docstring for trades
    """

    date = st.date_input("Choose a date")

    filename, real_date = find_most_recent_file_by_date(date)

    date = str_to_date(date)
    real_date = str_to_date(real_date, "%Y_%m_%d")

    if st.button("Run Trade Recap") :
        trade_recap_launcher(date)

    filename, real_date = find_most_recent_file_by_date(date)

    date = str_to_date(date)
    real_date = str_to_date(real_date, "%Y_%m_%d")

    if date != real_date :

        st.warning("No trade Recap generated for the selected Date")

    else :

        st.warning(f"Trade recap already geenrated for the selected date: {filename}")

        df, md5, _ = read_trade_recap_by_date(date, filename)
        
        min_cols = pick_default_columns(df, md5)


        st.divider()

        st.text("Master Trade Recap")
        st.data_editor((df.select(min_cols)))

        fun()

    return None






# -----------------------------
# Polars-first helpers
# -----------------------------

def pl_safe_upper(expr: pl.Expr) -> pl.Expr:
    return expr.cast(pl.Utf8).fill_null("").str.to_uppercase()


def df_to_csv_bytes(df: pl.DataFrame) -> bytes:
    # Polars native
    return df.write_csv().encode("utf-8")


def df_to_excel_bytes_polars_first(df: pl.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    """
    Excel export: Polars doesn't write xlsx directly in all setups,
    so we use pandas ONLY here (later you can switch to openpyxl direct).
    """
    import pandas as pd  # local import on purpose

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_pandas().to_excel(writer, sheet_name=sheet_name, index=False)
    return buf.getvalue()


def apply_user_review_defaults(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add helper columns for review + recaps.
    """
    if "Action" not in df.columns:
        df = df.with_columns(pl.lit("KEEP").alias("Action"))
    if "BookingTeam" not in df.columns:
        df = df.with_columns(pl.lit(None).cast(pl.Utf8).alias("BookingTeam"))
    if "Comments" not in df.columns:
        df = df.with_columns(pl.lit(None).cast(pl.Utf8).alias("Comments"))
    return df


def build_master_trade_recap_draft(
    date: dt.date,
    fund: str,
    source: str,
) -> Tuple[pl.DataFrame, Dict[str, Any]]:
    """
    STUB generator: replace later with your real ICE pipeline.
    """
    df = pl.DataFrame(
        {
            "TradeId": ["ICE-0001", "ICE-0002", "ICE-0003", "ICE-0004"],
            "ExecutionTime": [
                f"{date.isoformat()} 09:01:00",
                f"{date.isoformat()} 10:12:00",
                f"{date.isoformat()} 11:48:00",
                f"{date.isoformat()} 14:05:00",
            ],
            "ProductType": ["OTC", "FX", "OTC", "FUT"],
            "Ticker": ["AAPL", "EURUSD", "MSFT", "ES"],
            "Notional": [1_000_000, 5_000_000, 750_000, 2_000_000],
            "Currency": ["USD", "EUR", "USD", "USD"],
            "Counterparty": ["UBS", "UBS", "UBS", "CITI"],
        }
    )

    df = apply_user_review_defaults(df)

    meta = {"date": date.isoformat(), "fund": fund, "source": source, "rows": df.height}
    return df, meta


def normalize_review_filters(df: pl.DataFrame) -> pl.DataFrame:
    """
    Apply the 'Action' filter in a robust way.
    """
    if "Action" in df.columns:
        df = df.with_columns(pl.col("Action").cast(pl.Utf8).fill_null("KEEP").alias("Action"))
        df = df.filter(pl_safe_upper(pl.col("Action")) != "DROP")
    return df


def build_otc_recap_ubs(master_validated: pl.DataFrame) -> pl.DataFrame:
    """
    OTC recap (UBS):
      - Action != DROP
      - Counterparty == UBS (if exists)
      - prefer BookingTeam == OTC if user set it, else ProductType == OTC
    """
    df = normalize_review_filters(master_validated)

    if "Counterparty" in df.columns:
        df = df.filter(pl_safe_upper(pl.col("Counterparty")) == "UBS")

    if "BookingTeam" in df.columns:
        df_otc = df.filter(pl_safe_upper(pl.col("BookingTeam")) == "OTC")
        if df_otc.height > 0:
            return df_otc

    if "ProductType" in df.columns:
        return df.filter(pl_safe_upper(pl.col("ProductType")) == "OTC")

    return df.head(0)


def build_fx_recap_ubs(master_validated: pl.DataFrame) -> pl.DataFrame:
    """
    FX recap (UBS):
      - Action != DROP
      - Counterparty == UBS (if exists)
      - prefer BookingTeam == FX if set, else ProductType == FX
    """
    df = normalize_review_filters(master_validated)

    if "Counterparty" in df.columns:
        df = df.filter(pl_safe_upper(pl.col("Counterparty")) == "UBS")

    if "BookingTeam" in df.columns:
        df_fx = df.filter(pl_safe_upper(pl.col("BookingTeam")) == "FX")
        if df_fx.height > 0:
            return df_fx

    if "ProductType" in df.columns:
        return df.filter(pl_safe_upper(pl.col("ProductType")) == "FX")

    return df.head(0)


def _pl_from_editor_output(edited: Any) -> pl.DataFrame:
    """
    st.data_editor is not Polars-native. We keep Polars as the internal source of truth.
    """
    if edited is None:
        return pl.DataFrame()

    if isinstance(edited, list):
        # list[dict] -> Polars (best case)
        return pl.DataFrame(edited)

    # pandas df fallback
    try:
        import pandas as pd
        if isinstance(edited, pd.DataFrame):
            return pl.from_pandas(edited)
    except Exception:
        pass

    return pl.DataFrame(edited)


def st_table_from_polars(df: pl.DataFrame, *, height: int = 350):
    """
    Streamlit doesn't always render Polars perfectly; convert only at display-time.
    """
    try:
        st.dataframe(df, use_container_width=True, hide_index=True, height=height)
    except Exception:
        st.dataframe(df.to_pandas(), use_container_width=True, hide_index=True, height=height)


# -----------------------------
# Streamlit App
# -----------------------------

def fun () :
        
    # Session state
    st.session_state.setdefault("draft_df", None)        # pl.DataFrame
    st.session_state.setdefault("validated_df", None)    # pl.DataFrame
    st.session_state.setdefault("meta", {})              # dict

    # Controls
    c1, c2, c3, c4 = st.columns([1.2, 0.9, 1.0, 1.3], vertical_alignment="bottom")
    with c1:
        recap_date = st.date_input("Date", value=dt.date.today())
    with c2:
        fund = st.selectbox("Fund", options=["HV", "WR"], index=0)
    with c3:
        source = st.selectbox("Source", options=["ICE (files)", "ICE (API)"], index=0)
    with c4:
        st.markdown("**Steps:** 2.1 → 2.2 → 2.3 → 2.4/2.5")

    st.divider()

    # 2.1 Build draft
    left, right = st.columns([1.0, 2.0], vertical_alignment="center")
    with left:
        if st.button("▶️ Build Master Trade Recap (Draft)", use_container_width=True):
            df, meta = build_master_trade_recap_draft(recap_date, fund, source)
            st.session_state["draft_df"] = df
            st.session_state["validated_df"] = None
            st.session_state["meta"] = meta

    with right:
        meta = st.session_state.get("meta") or {}
        if st.session_state["draft_df"] is None:
            st.info("No draft yet. Click **Build** to generate a draft (stub data for now).")
        else:
            st.success(f"Draft ready — {st.session_state['draft_df'].height} rows")
            st.caption(f"Meta: {meta}")

    draft_df: Optional[pl.DataFrame] = st.session_state["draft_df"]
    validated_df: Optional[pl.DataFrame] = st.session_state["validated_df"]

    st.divider()

    # 2.2 Review
    st.subheader("2.2 Review (Add / Modify / Remove)")

    if draft_df is None:
        st.warning("Build a draft first.")
        st.stop()

    tool1, tool2, tool3, tool4 = st.columns([1.0, 1.0, 1.0, 2.0], vertical_alignment="bottom")
    with tool1:
        allow_add = st.checkbox("Allow add rows", value=True)
    with tool2:
        allow_delete = st.checkbox("Allow delete rows", value=True)
    with tool3:
        freeze_key_cols = st.checkbox("Freeze key cols", value=True)
    with tool4:
        st.caption("Use BookingTeam=OTC/FX or Action=DROP to control downstream recaps.")

    disabled_cols: List[str] = []
    if freeze_key_cols:
        for col in ["TradeId", "ExecutionTime"]:
            if col in draft_df.columns:
                disabled_cols.append(col)

    # Streamlit editor expects dicts/pandas-like. Convert ONLY for editor input.
    draft_for_editor = draft_df.to_dicts()

    edited = st.data_editor(
        draft_for_editor,
        use_container_width=True,
        num_rows="dynamic" if allow_add else "fixed",
        disabled=disabled_cols,
        hide_index=True,
    )

    edited_df = _pl_from_editor_output(edited)

    # Apply Action filter in Polars
    edited_df = normalize_review_filters(edited_df)

    st.caption(f"After review: **{edited_df.height}** rows")

    st.markdown("#### Preview (reviewed)")
    st_table_from_polars(edited_df, height=300)

    st.divider()

    # 2.3 Validate
    st.subheader("2.3 Validate Master Trade Recap (freeze snapshot)")

    v1, v2, v3 = st.columns([1.2, 1.2, 2.0], vertical_alignment="center")
    with v1:
        if st.button("✅ Validate (create final Master)", type="primary", use_container_width=True):
            st.session_state["validated_df"] = edited_df
            st.success("Validated Master created (snapshot frozen).")

    with v2:
        if st.button("♻️ Reset validation", use_container_width=True):
            st.session_state["validated_df"] = None
            st.warning("Validation reset.")

    with v3:
        if st.session_state["validated_df"] is None:
            st.info("Not validated yet. Validation is required before generating OTC/FX recaps.")
        else:
            st.success(f"Validated Master ready — {st.session_state['validated_df'].height} rows")

    st.divider()

    # Master exports
    st.subheader("Master Export")

    export_df = st.session_state["validated_df"] if st.session_state["validated_df"] is not None else edited_df

    e1, e2, e3 = st.columns([1.0, 1.0, 2.0], vertical_alignment="bottom")
    with e1:
        st.download_button(
            "⬇️ Download Master (Excel)",
            data=df_to_excel_bytes_polars_first(export_df, sheet_name="Master"),
            file_name=f"Master_Trade_Recap_{fund}_{recap_date.isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with e2:
        st.download_button(
            "⬇️ Download Master (CSV)",
            data=df_to_csv_bytes(export_df),
            file_name=f"Master_Trade_Recap_{fund}_{recap_date.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with e3:
        st.caption("Uses validated Master if available; otherwise uses the reviewed draft.")

    st.divider()

    # 2.4 / 2.5 Recaps
    st.subheader("2.4 OTC Trade Recap UBS  |  2.5 FX Trade Recap UBS")

    base = st.session_state["validated_df"]
    if base is None:
        st.warning("Validate the Master first to generate OTC/FX recaps.")
        st.stop()

    r1, r2 = st.columns(2, vertical_alignment="top")

    with r1:
        st.markdown("### OTC Recap (UBS)")
        otc_df = build_otc_recap_ubs(base)
        st_table_from_polars(otc_df, height=320)

        st.download_button(
            "⬇️ Download OTC (Excel)",
            data=df_to_excel_bytes_polars_first(otc_df, sheet_name="OTC"),
            file_name=f"UBS_OTC_Recap_{fund}_{recap_date.isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download OTC (CSV)",
            data=df_to_csv_bytes(otc_df),
            file_name=f"UBS_OTC_Recap_{fund}_{recap_date.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with r2:
        st.markdown("### FX Recap (UBS)")
        fx_df = build_fx_recap_ubs(base)
        st_table_from_polars(fx_df, height=320)

        st.download_button(
            "⬇️ Download FX (Excel)",
            data=df_to_excel_bytes_polars_first(fx_df, sheet_name="FX"),
            file_name=f"UBS_FX_Recap_{fund}_{recap_date.isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download FX (CSV)",
            data=df_to_csv_bytes(fx_df),
            file_name=f"UBS_FX_Recap_{fund}_{recap_date.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )




