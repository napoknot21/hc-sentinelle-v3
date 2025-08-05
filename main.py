import streamlit as st
from datetime import datetime as dt

from src.config.parameters import FUND_WR, FUND_HV

from src.core.api.simm import read_simm_history_from_excel, load_simm_data, update_simm_history_from_df

st.title("Test SIMM API")

#st.dataframe(load_simm_data( dt.strptime("2025-08-05", "%Y-%m-%d")))

df, hash = read_simm_history_from_excel(FUND_HV)
update_df = update_simm_history_from_df(df, hash)
st.dataframe(update_df)

df_2, hashh = load_simm_data()

st.dataframe(df_2)