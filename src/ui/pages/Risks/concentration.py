from __future__ import annotations

import datetime as dt
import streamlit as st

from typing import Optional

from src.core.data.concentration import read_ccty_concentration

from src.ui.components.text import center_h2


def concentration (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("Concentration")
    concentration_distribution(date, fundation)

    return None



def concentration_distribution (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    col1, col2 = st.columns(2)

    with col1 :
        ccty_distribution_abs_section(date, fundation)

    with col2 :
        ccty_distribution_mv_nav_section(date, fundation)

    return None



def ccty_distribution_abs_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    dataframe, md5 = read_ccty_concentration(date, fundation)
    st.dataframe(dataframe)
    return None


def ccty_distribution_mv_nav_section (
    
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    dataframe, md5 = read_ccty_concentration(date, fundation)
    st.dataframe(dataframe)
    return None