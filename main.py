import streamlit as st
from datetime import datetime as dt

from src.core.api.simm import get_ice_calculator, get_simm

st.title("Test SIMM API")

get_simm(dt.now(), "Heroics Volitility Fund")

