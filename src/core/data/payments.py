from __future__ import annotations

import polars as pl
import datetime as dt

from typing import Optional, Dict, List

from src.config.parameters import PAYMENTS_COLUMNS, SECURITIES_COLUMNS, PAYMENTS_BENEFICIARY_COLUMNS, PAYMENTS_BENECIFIARY_SHEET_NAME
from src.config.paths import (
    PAYMENTS_DB_ABS_PATH, PAYMENTS_DB_REL_PATH,
    SECURITIES_DB_REL_PATH, PAYMENTS_BENECIFIARY_DB_ABS_PATH
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


def load_beneficiaries_db (
        
        file_abs_path : Optional[str] = None,
        sheet_name :  Optional[str] = None,
        schema_overrides : Optional[Dict] = None,
        
    ) :
    """
    
    """
    file_abs_path = PAYMENTS_BENECIFIARY_DB_ABS_PATH if file_abs_path is None else file_abs_path
    sheet_name = PAYMENTS_BENECIFIARY_SHEET_NAME if sheet_name is None else sheet_name

    schema_overrides = PAYMENTS_BENEFICIARY_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    dataframe, md5 = load_excel_to_dataframe(file_abs_path, sheet_name=sheet_name, schema_overrides=schema_overrides, specific_cols=specific_cols)

    return dataframe, md5


def find_beneficiary_by_ctpy_ccy_n_type (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        counterparty : Optional[str] = None,
        type_ben : Optional[str] = None,
        currency : Optional[str] = None,
        #bank_name : Optional[str] = None,

        columns : Optional[Dict] = None,

    ) :
    """
    
    """
    dataframe, _ = load_beneficiaries_db() if dataframe is None else dataframe
    columns = PAYMENTS_BENEFICIARY_COLUMNS if columns is None else columns

    specific_cols = list(columns.keys())[:3]

    if counterparty is None or type_ben is None or currency is None :
        return None

    df_match = (

        dataframe
        .filter(

            (pl.col(specific_cols[0]) == counterparty) &
            (pl.col(specific_cols[1]) == type_ben) &
            (pl.col(specific_cols[2]) == currency)

        )

    )

    if df_match.is_empty() :
        return None
    
    last_values = list(columns.keys())[3:]
    
    row = df_match.row(0)

    benef_bank  = row[3]
    swift_code  = row[4]
    swift_ben   = row[5]
    iban        = row[6]

    print(row)

    return swift_code, benef_bank, swift_ben, iban




