from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import Optional

from src.utils.formatters import date_to_str

#from src.core.api.simm import *
from src.core.data.simm import get_simm_by_date

from src.ui.components.text import center_h2
from src.ui.components.charts import simm_ctpy_im_vm_chart

def simm (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("SIMM")
    
    realized_var_cvar_section(date, fundation)
    return None


def realized_var_cvar_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None

    ) :
    """
    
    """
    dataframe, md5 = get_simm_by_date(date, fundation)

    date = date_to_str(date)
    fig = simm_ctpy_im_vm_chart(dataframe, md5, date, "Counterparty", ("IM", "MV"))

    st.plotly_chart(fig, use_container_width=True)


