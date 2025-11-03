from __future__ import annotations

import polars as pl
import datetime as dt

from typing import Optional, Dict, List

from src.config.parameters import PAYMENTS_COLUMNS, SECURITIES_COLUMNS
from src.config.paths import (
    PAYMENTS_DB_ABS_PATH, PAYMENTS_DB_REL_PATH,
    SECURITIES_DB_REL_PATH
)
from src.utils.data_io import load_excel_to_dataframe


def load_payments_db (
        
        file_abs_path : Optional[str] = None,
        schema_overrides : Optional[Dict] = None,

    ) -> tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    file_abs_path = PAYMENTS_DB_REL_PATH if file_abs_path is None else file_abs_path

    schema_overrides = PAYMENTS_COLUMNS if schema_overrides is None else schema_overrides
    columns = list(schema_overrides.keys())

    dataframe, md5 = load_excel_to_dataframe(

        file_abs_path,
        schema_overrides=schema_overrides,
        specific_cols=columns,
        cast_num=False
    
    )

    return dataframe, md5


def order_payments_by_column (dataframe : Optional[pl.DataFrame], md5 : Optional[str] = None, column : Optional[str] = None) :
    """
    
    """
    if dataframe is None :    
        return None, None
    


def load_securities_db (

        file_abs_path : Optional[str] = None,
        schema_overrides : Optional[str] = None,    

    ) -> tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    file_abs_path = SECURITIES_DB_REL_PATH if file_abs_path is None else file_abs_path

    schema_overrides = SECURITIES_COLUMNS if schema_overrides is None else schema_overrides
    columns = list(schema_overrides.keys())

    dataframe, md5 = load_excel_to_dataframe(

        file_abs_path,
        schema_overrides=schema_overrides,
        specific_cols=columns,
        cast_num=False
    
    )

    return dataframe, md5
