from __future__ import annotations

import streamlit as st
import datetime as dt

from src.config.parameters import *
from src.config.paths import *
from src.utils.logger import log
from src.core.data.expiries import *
#from src.core.data.simm import read_simm_history_from_excel
from src.ui.pages.Payments.security import *

def render_payments () :
    """
    Main function that displays the Payments page
    """
    # Default date: today
    selected_date : dt.date = st.date_input("Select date", value=dt.date.today())

    #df_simm = read_simm_history_from_excel(FUND_HV)
    file_abs_path = get_most_recent_file_for_date(selected_date, FUND_HV, EXPIRIES_FUNDS_DIR_PATHS, EXPIRIES_FILENAME_REGEX)

    #if file_abs_path is None :
    #    file_abs_path = get_most_recent_file(FUND_HV, EXPIRIES_FUNDS_DIR_PATHS, EXPIRIES_FILENAME_REGEX)

    # Load and display dataframe
    try:

        df, _ = load_upcomming_expiries(selected_date, FUND_HV, )

    except Exception as e:
        
        message = f"Failed to load expiries: {e}"
        
        st.error(message)
        log(message=message, level="error")
        
        return
    
    st.warning(f"Used file from : {file_abs_path}")
    
    if df is not None :
        st.dataframe(df, use_container_width=True)
        #st.dataframe(df_simm, use_container_width=True)
    else:    
        st.info("No expiries found for the selected date.")