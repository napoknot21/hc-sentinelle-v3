import os, sys
import streamlit as st

from src.utils.logger import log
from src.config.paths import LIBAPI_ABS_PATH
sys.path.append(LIBAPI_ABS_PATH)

from libapi.pricers.fx import PricerFX # type:ignore
from libapi.pricers.eq import PricerEQ # type:ignore

from libapi.ice.calculator import IceCalculator # type:ignore
from libapi.ice.trade_manager import TradeManager# type:ignore


# Function to initialize the API
#@st.cache_resource()
def get_ice_calculator (loopback : int = 3) :
    """
    Initializes and returns a cached instance of IceCalculator.
    
    :param loopback: Number of retries connections
    :type loopback: int
    
    Returns:
        IceCalculator: An instance of the IceCalculator class used for ICE-related computations.
    """
    ice_calculator = None
    
    if loopback < 0 :

        log("[-] Connection failed to API Calculator after serveral retries.", "error")
        return ice_calculator

    try :
        
        ice_calculator = IceCalculator()
        log("[+] LibAPI successfully connected")

    except :

        print("[-] Error during LibAPI connection. Retrying...", "error")
        return get_ice_calculator(loopback - 1)

    return ice_calculator


#@st.cache_resource()
def get_trade_manager (loopback : int = 3) :
    """
    Initializes and returns a cached instance of TradeManager.

    Returns:
        TradeManager: An instance of the TradeManager class responsible for managing ICE trades.
    """
    trade_manager = None

    if loopback < 0 :

        log("[-] Connection failed to API for Trade Manager after serveral retries.", "error")
        return trade_manager
    
    try :

        trade_manager = TradeManager()
        log("[+] LibAPI successfully connected")

    except :

        print("[-] Error during LibAPI connection. Retrying...", "error")
        return get_trade_manager(loopback - 1)

    return trade_manager


#@st.cache_resource()
def get_pricer_fx () :
    """
    Initializes and returns a cached instance of PricerFX.

    Returns:
        PricerFX: An instance of the FX pricer used for foreign exchange pricing operations.
    """
    pricer_fx = PricerFX()

    return pricer_fx


#@st.cache_resource()
def get_pricer_eq () :
    """
    Initializes and returns a cached instance of PricerEQ.

    Returns:
        PricerEQ: An instance of the EQ pricer used for equity pricing operations.
    """
    pricer_eq = PricerEQ()

    return pricer_eq