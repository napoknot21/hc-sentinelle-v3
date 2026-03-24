from __future__ import annotations

import os
import polars as pl
import datetime as dt

from typing import List, Optional, Dict

from src.utils.logger import log
from src.utils.data_io import load_excel_to_dataframe, export_dataframe_to_excel
from src.utils.formatters import str_to_date

from src.config.paths import SIMM_FUNDS_DIR_PATHS
from src.config.parameters import (
    FUND_HV, SIMM_HIST_NAME_DEFAULT, SIMM_CUTOFF_DATE, SIMM_MAPPING_COUNTERPARTIES, SIMM_HISTORY_COLUMNS
)


def _empty_simm_history_dataframe (

        schema_overrides : Optional[Dict] = None
    
    ) -> pl.DataFrame :
    """
    Build an empty SIMM history dataframe with the expected schema.
    """
    schema_overrides = SIMM_HISTORY_COLUMNS if schema_overrides is None else schema_overrides
    dataframe = pl.DataFrame(schema=schema_overrides)

    return dataframe 


def get_simm_all_history (
        
        fund : Optional[str ] = None,
        paths_by_fund : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,
        columns : Optional[List[str]] = None,

        cutoff_date : Optional[str | dt.datetime | dt.date] = None
        
    ) :
    """
    
    """
    fund = FUND_HV if fund is None else fund
    paths_by_fund = SIMM_FUNDS_DIR_PATHS if paths_by_fund is None else paths_by_fund
    
    schema_overrides = SIMM_HISTORY_COLUMNS if schema_overrides is None else schema_overrides
    columns = list(schema_overrides.keys()) if columns is None else columns

    file_abs_path = get_simm_abs_path_by_fund(fund)

    if file_abs_path is None :
        return _empty_simm_history_dataframe(schema_overrides), None

    try :
        dataframe, md5 = load_excel_to_dataframe(file_abs_path, specific_cols=columns, schema_overrides=schema_overrides) 

    except Exception as e :
        return None, None
    
    cutoff_date = str_to_date(SIMM_CUTOFF_DATE if cutoff_date is None else cutoff_date)

    dataframe = dataframe.filter(pl.col("Date") >= (cutoff_date))
    
    return dataframe, md5


def get_simm_by_date_from_history (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund : Optional[str] = None,
        paths_by_fund : Optional[Dict] = None,

        schema_overrides : Optional[Dict] = None,
        columns : Optional[List] = None,
        
        cutoff_date : Optional[str] = None

    ) :
    """
    Get all conterparties SIMM for a selected Date
    """
    fund = FUND_HV if fund is None else fund
    paths_by_fund = SIMM_FUNDS_DIR_PATHS if paths_by_fund is None else paths_by_fund

    schema_overrides = SIMM_HISTORY_COLUMNS if schema_overrides is None else schema_overrides
    columns = list(schema_overrides.keys()) if columns is None else columns

    cutoff_date = str_to_date(SIMM_CUTOFF_DATE if cutoff_date is None else cutoff_date)

    dataframe, md5 = get_simm_all_history(fund, paths_by_fund, schema_overrides, columns, cutoff_date) if dataframe is None else (dataframe, md5)

    if dataframe is None or dataframe.is_empty() :
        return None, None
    
    date = str_to_date(date)
    dataframe = dataframe.filter(pl.col("Date") == date)

    return dataframe, md5


def update_simm_history(
        
        new_rows : Optional[pl.DataFrame] = None,

        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        fund : Optional[str] = None,
        paths_by_fund : Optional[Dict] = None,

        schema_overrides : Optional[Dict] = None,
        columns : Optional[List[str]] = None,

        cutoff_date : Optional[str | dt.datetime | dt.date] = None,
        sort_result : bool = True,

    ) -> bool :
    """
    Update full SIMM history by inserting new rows for a given date.

    Assumption
    ----------
    `new_rows` already has the SIMM history structure, i.e. all columns from
    `SIMM_HISTORY_COLUMNS`.

    Behavior
    --------
    - load full history
    - optionally overwrite `Date` in `new_rows`
    - optionally remove existing rows for that date
    - append new rows
    - optionally deduplicate / sort
    """
    fund = FUND_HV if fund is None else fund
    paths_by_fund = SIMM_FUNDS_DIR_PATHS if paths_by_fund is None else paths_by_fund

    schema_overrides = SIMM_HISTORY_COLUMNS if schema_overrides is None else schema_overrides
    columns = list(schema_overrides.keys()) if columns is None else columns

    if new_rows is None or new_rows.is_empty() :

        log("[!] New rows are None or empty... Nothing updated", "warning")
        return False
    
    # Normalization
    new_rows = (new_rows.select(columns).cast(schema_overrides, strict=False))

    cutoff_date = str_to_date(SIMM_CUTOFF_DATE if cutoff_date is None else cutoff_date)
    dataframe, md5 = get_simm_all_history(fund, paths_by_fund, schema_overrides, columns, cutoff_date) if dataframe is None else (dataframe, md5)
    
    file_abs_path = get_simm_abs_path_by_fund(fund, paths_by_fund)

    if dataframe is None or dataframe.is_empty() :

        status = export_dataframe_to_excel(new_rows, output_abs_path=file_abs_path)
        log(f"{status.get("message")}")

        return status.get("success")
    
    # Here dataframe already exists and new_rows is in good foramt.
    dataframe = pl.concat([dataframe, new_rows], how="diagonal_relaxed")

    if sort_result :
        dataframe = dataframe.sort("Date")

    result = export_dataframe_to_excel(dataframe, output_abs_path=file_abs_path)
    log(result.get("message"))
        
    return result.get("success", False)


def get_simm_abs_path_by_fund (
        
        fund : Optional[str] = None,
        simm_fund_paths : Optional[Dict] = None,
        basename_file : Optional[str] = None

    ) -> Optional[str] :
    """
    Resolve the history workbook path for the requested fund.
    """
    fund = FUND_HV if fund is None else fund
    simm_fund_paths = SIMM_FUNDS_DIR_PATHS if simm_fund_paths is None else simm_fund_paths
    basename_file = SIMM_HIST_NAME_DEFAULT if basename_file is None else basename_file

    file_abs_directory = simm_fund_paths.get(fund)
    if not file_abs_directory :
        return None

    file_abs_path = os.path.join(file_abs_directory, basename_file)

    return file_abs_path


def rename_ancien_simm_counterparties (
        
        dataframe : Optional[pl.DataFrame] = None,
        rename_mapping : Optional[Dict] = None,
        column : Optional[str] = "Counterparty"

    ) -> Optional[pl.DataFrame] :
    """
    Harmonize historical counterparty labels.
    """
    if dataframe is None :

        log("[-] No dataframe provided for renaming.", "error")
        return None
    
    rename_mapping = SIMM_MAPPING_COUNTERPARTIES if rename_mapping is None else rename_mapping

    dataframe = dataframe.with_columns(
        pl.col(column).cast(pl.Utf8).replace(rename_mapping).alias(column)
    )

    return dataframe
