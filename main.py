import streamlit as st
import datetime as dt

from src.config.parameters import FUND_NAME_MAP

from src.core.api.simm import fetch_raw_simm_data

st.title("Test SIMM API")

#st.dataframe(load_simm_data( dt.strptime("2025-08-05", "%Y-%m-%d")))

#df, hash = read_simm_history_from_excel(FUND_HV)
#update_df = update_simm_history_from_df(df, hash)
#st.dataframe(update_df)

#df_2, hashh = load_simm_data()

#st.dataframe(df_2)"""
date = st.date_input("Date à récupérer", dt.datetime.now().strftime("%Y-%m-%d"))
print(type(date))
print(type(dt.datetime.now()))
dt = dt.datetime.combine(date, dt.time())
print(dt)
print(type(dt))
fund = st.selectbox("Fundation", options=list(FUND_NAME_MAP.keys()))

result = fetch_raw_simm_data(dt, fund)

if result:
    df, df_hash = result
    st.dataframe(df)
    st.write(f"Hash: {df_hash}")

else:
    st.warning("Aucune donnée retournée.")