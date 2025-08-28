import streamlit as st
import datetime as dt

from src.core.data.expiries import load_upcomming_expiries_from_file, get_most_recent_file_for_date, get_most_recent_file
from src.ui.pages.Payments.security import *

def render_payments () :
    """
    Main function that displays the Payments page
    """
    # Default date: today
    selected_date : dt.date = st.date_input("Select date", value=dt.date.today())

    file_abs_path = get_most_recent_file_for_date(selected_date)

    if file_abs_path is None :
        file_abs_path = get_most_recent_file()

    # Load and display dataframe
    try:

        df = load_upcomming_expiries_from_file(file_abs_path, date=selected_date)

    except Exception as e:
        
        st.error(f"Failed to load expiries: {e}")
        return
    
    st.warning(f"Used file from : {file_abs_path}")
    
    if df is not None :
        print(df.dtypes)
        st.dataframe(df, use_container_width=True)
    
    else:
    
        st.info("No expiries found for the selected date.")