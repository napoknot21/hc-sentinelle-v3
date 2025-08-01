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
    Initializes and returns a cached instance of IceCalculator.

    Returns:
        IceCalculator: An instance of the IceCalculator class used for ICE-related computations.
    """

    ice_calculator = IceCalculator()

    return ice_calculator


@st.cache_resource()
def get_trade_manager () :
    """
    Initializes and returns a cached instance of TradeManager.

    Returns:
        TradeManager: An instance of the TradeManager class responsible for managing ICE trades.
    """
    trade_manager = TradeManager()
    
    return trade_manager


@st.cache_resource()
def get_pricer_fx () :
    """
    Initializes and returns a cached instance of PricerFX.

    Returns:
        PricerFX: An instance of the FX pricer used for foreign exchange pricing operations.
    """
    pricer_fx = PricerFX()

    return pricer_fx


@st.cache_resource()
def get_pricer_eq () :
    """
    Initializes and returns a cached instance of PricerEQ.

    Returns:
        PricerEQ: An instance of the EQ pricer used for equity pricing operations.
    """
    pricer_eq = PricerEQ()

    return pricer_eq