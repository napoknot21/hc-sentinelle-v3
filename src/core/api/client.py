import os, sys
import streamlit as st

from src.config.paths import LIBAPI_PATH
sys.path.append(str(LIBAPI_PATH))

from libApi.pricers.fx import PricerFX
from libApi.pricers.eq import PricerEQ

from libApi.ice.ice_calculator import IceCalculator
from libApi.ice.trade_manager import TradeManager


# Function to initialize the API
@st.cache_resource()
def get_ice_calculator () :
    """
    
    """
    ice_calculator = IceCalculator()

    return ice_calculator


@st.cache_resource()
def get_trade_manager () :
    """
    
    """
    trade_manager = TradeManager()
    
    return trade_manager


@st.cache_resource()
def get_pricer_fx () :
    """
    
    """
    pricer_fx = PricerFX()

    return pricer_fx


@st.cache_resource()
def get_pricer_eq () :
    """
    
    """
    pricer_eq = PricerEQ()

    return pricer_eq