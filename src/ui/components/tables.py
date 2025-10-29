from __future__ import annotations

import datetime as dt
import polars as pl
import pandas as pd

from typing import List, Optional

import streamlit as st
from st_aggrid import AgGrid


@st.cache_data()
def show_last_n_expiries (_dataframe : pl.DataFrame, md5 : str, specific_cols : Optional[List[str]], max_rows : int = 10) :
    """
    
    """
    _dataframe = _dataframe.select(specific_cols) if specific_cols is not None else _dataframe
    df_head = _dataframe.head(max_rows)

    table = st.dataframe(df_head)
    return table


@st.cache_data()
def show_full_expiries (_dataframe : pl.DataFrame, md5 : str, ) :
    """
    
    """
    return None