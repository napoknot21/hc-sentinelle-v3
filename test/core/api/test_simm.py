import pytest
from unittest.mock import patch, MagicMock
import polars as pl
from src.core.api.simm import get_simm, get_simm_data
from src.utils.logger import log

from src.config.parameters import FUND_HV, FUND_WR, FUND_NAME_MAP

