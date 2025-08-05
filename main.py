import streamlit as st
from datetime import datetime as dt

from src.config.parameters import FUND_WR

from src.core.api.simm import read_simm_history_from_excel, load_simm_data

st.title("Test SIMM API")

st.dataframe(load_simm_data( dt.strptime("2025-08-05", "%Y-%m-%d")))

