from __future__ import annotations

import os
import re
import polars as pl
import datetime as dt


from typing import Optional, List, Dict, Tuple

from src.utils.logger import log
from src.utils.formatters import date_to_str, str_to_date
from src.utils.data_io import load_excel_to_dataframe
from src.config.parameters import (
    FUND_HV,
    GREEKS_ALL_FILENAME, GREEKS_COLUMNS, GREEKS_REGEX, GREEKS_OVERVIEW_COLUMNS,
    GREEKS_GAMMA_PNL_COLUMNS, GREEKS_GAMMA_PNL_REGEX,
    GREEKS_VEGA_BUCKET_COLUMNS, GREEKS_VEGA_STRESS_PNL_COLUMNS, GREEKS_VEGA_STRESS_PNL_REGEX,
    GREEKS_VEGA_BUCKET_REGEX, GREEKS_ASSET_CLASS_RULES,
    GREEKS_DELTA_PNL_STRESS_COLUMNS, GREEKS_DELTA_PNL_STRESS_REGEX, GREEKS_DELTA_STRESS_NAV_REGEX,
    GREEKS_LONG_SHORT_DELTA_COLUMNS, GREEKS_LONG_SHORT_DELTA_REGEX, GREEKS_DELTA_STRESS_NAV_COLUMNS,
    GREEKS_DELTA_STRESS_ABS_COLUMNS, GREEKS_DELTA_STRESS_ABS_REGEX, GREEKS_RISK_CREDIT_COLUMNS,
    GREEKS_RISK_CREDIT_REGEX, GREEKS_RISKS_EQUITY_COLUMNS
)
from src.config.paths import (
    GREEKS_FUNDS_DIR_PATHS, GREEKS_GAMMA_PNL_FUNDS_DIR_PATHS,
    GREEKS_VEGA_BUCKET_FUNDS_DIR_PATHS, GREEKS_VEGA_STRESS_PNL_FUNDS_DIR_PATHS,
    GREEKS_DELTA_STRESS_ABS_FUNDS_DIR_PATHS, GREEKS_DELTA_STRESS_NAV_FUNDS_DIR_PATHS,
    GREEKS_LONG_SHORT_DELTA_FUNDS_DIR_PATHS, GREEKS_DELTA_PNL_STRESS_FUNDS_DIR_PATHS,
    GREEKS_RISK_CREDIT_FUNDS_DIR_PATHS, GREEKS_RISK_EQUITY

)

def read_history_greeks (

        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        greeks_paths : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    schema_overrides = GREEKS_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    greeks_paths = GREEKS_FUNDS_DIR_PATHS if greeks_paths is None else greeks_paths
    filename = GREEKS_ALL_FILENAME if filename is None else filename

    dir_abs = greeks_paths.get(fund)
    full_path = os.path.join(dir_abs, filename)

    try :
        dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides, specific_cols=specific_cols)

    except Exception as e :
        
        log("[-] Error during greeks history file reading", "error")
        return None, None
    
    return dataframe, md5


def read_greeks_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        greeks_paths : Optional[Dict] = None,
        
        schema_overrides : Optional[Dict] = None,
        regex : Optional[re.Pattern] = None,
        mode : str = "eq"

    ) -> Tuple[Optional[pl.DataFrame], Optional[str], Optional[str]] :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    schema_overrides = GREEKS_OVERVIEW_COLUMNS if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    regex = GREEKS_REGEX if regex is None else regex

    greeks_paths = GREEKS_FUNDS_DIR_PATHS if greeks_paths is None else greeks_paths
    dir_abs = greeks_paths.get(fund)

    filename, real_date = find_most_recent_file_by_date(date, dir_abs, regex, mode=mode) if filename is None else filename
    
    if filename is None :
        return None, None, None

    full_path = os.path.join(dir_abs, filename)

    try :
        dataframe, md5 = load_excel_to_dataframe(full_path, schema_overrides=schema_overrides, specific_cols=specific_cols)

    except Exception as e :
        
        log(f"[-] Error during greeks {date_to_str(date)} file reading", "error")
        return None, None, None
    
    return dataframe, md5, real_date


def find_most_recent_file_by_date (
    
        date : Optional[str | dt.datetime | dt.date] = None,

        dir_abs_path : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

        mode: str = "eq",  # "eq", "le", "ge"
    
    ) -> Tuple[Optional[str], Tuple[str]] :
    """
    Return
    """
    date_str_target = date_to_str(date)

    if not os.path.isdir(dir_abs_path) :
        return None, None
    
    # Best pour la date cible
    best_per_date: Dict[str, Tuple[int, int, float, str]] = {}

    with os.scandir(dir_abs_path) as it : # 
        
        for entry in it :

            if not entry.is_file() :
                continue
            
            m = regex.match(entry.name)

            if not m :
                continue

            date_str, hh, mm = m.groups()

            hh_i = int(hh)
            mm_i = int(mm)

            mtime = entry.stat().st_mtime

            key = (hh_i, mm_i, mtime)

            current = best_per_date.get(date_str)

            if current is None or key > current[:3] :
                best_per_date[date_str] = (hh_i, mm_i, mtime, entry.name)

    if not best_per_date:
        return None, None
    
    # Si on a exactement la date cible, on la privilégie pour tous les modes
    if date_str_target in best_per_date:
        _, _, _, fname = best_per_date[date_str_target]
        return fname, date_str_target

    # Pas de fichier pour la date exacte -> on applique le "mode"
    all_dates = sorted(best_per_date.keys())  # tri lexical = tri chronologique

    if mode == "eq":
        # strict : rien trouvé à la date exacte
        return None, None

    elif mode == "le":
        # last date <= date target
        candidates = [d for d in all_dates if d <= date_str_target]

        if not candidates:
            return None, None
        chosen_date = candidates[-1]

    elif mode == "ge":
        # First date >= date Target
        candidates = [d for d in all_dates if d >= date_str_target]
        if not candidates:
            return None, None
        chosen_date = candidates[0]

    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'eq', 'le' or 'ge'.")

    _, _, _, fname = best_per_date[chosen_date]

    return fname, chosen_date


# ----------------- Scripts and analysis -----------------


def delta_stress_scenarios () :
    """
    Docstring for delta_stress_scenarios
    """

    return None



def gamma_pnl (

        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None,    
        schema_overrides : Optional[Dict] = None,

        mode : str = "le"
    ) :
    """
    Docstring for gamma_pnl
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_GAMMA_PNL_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund

    regex = GREEKS_GAMMA_PNL_REGEX if regex is None else regex
    schema_overrides = GREEKS_GAMMA_PNL_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)
    dataframe = dataframe.filter(pl.col("Underlying") != "Total")

    return dataframe, md5, real_date


def delta_pnl_stress (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None,

        schema_overrides : Optional[Dict] = None,
        mode : str = "le"
    
    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_DELTA_PNL_STRESS_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund

    regex = GREEKS_DELTA_PNL_STRESS_REGEX if regex is None else regex
    schema_overrides = GREEKS_DELTA_PNL_STRESS_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)

    dataframe = dataframe.fill_nan(None)

    nulls = dataframe.null_count().row(0)
    keep_cols = [c for c, n in zip(dataframe.columns, nulls) if n < dataframe.height]
    dataframe = dataframe.select(keep_cols)

    dataframe = dataframe.filter(pl.any_horizontal(pl.all().is_not_null()))

    return dataframe, md5, real_date


def delta_stress_nav (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None,

        schema_overrides : Optional[Dict] = None,
        mode : str = "le"
    
    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_DELTA_STRESS_NAV_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund

    regex = GREEKS_DELTA_STRESS_NAV_REGEX if regex is None else regex
    schema_overrides = GREEKS_DELTA_STRESS_NAV_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)

    if dataframe is None  :
        return None, None, None
    
    dataframe = dataframe.fill_nan(None)

    nulls = dataframe.null_count().row(0)
    keep_cols = [c for c, n in zip(dataframe.columns, nulls) if n < dataframe.height]
    dataframe = dataframe.select(keep_cols)

    dataframe = dataframe.filter(pl.any_horizontal(pl.all().is_not_null()))

    return dataframe, md5, real_date


def delta_stress_abs (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None,

        schema_overrides : Optional[Dict] = None,
        mode : str = "le"
    
    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_DELTA_STRESS_ABS_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund

    regex = GREEKS_DELTA_STRESS_ABS_REGEX if regex is None else regex
    schema_overrides = GREEKS_DELTA_STRESS_ABS_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)

    if dataframe is None  :
        return None, None, None
    
    dataframe = dataframe.fill_nan(None)

    nulls = dataframe.null_count().row(0)
    keep_cols = [c for c, n in zip(dataframe.columns, nulls) if n < dataframe.height]
    dataframe = dataframe.select(keep_cols)

    dataframe = dataframe.filter(pl.any_horizontal(pl.all().is_not_null()))

    return dataframe, md5, real_date



def long_short_delta (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None,    
        schema_overrides : Optional[Dict] = None,

        mode : str = "le"

    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_LONG_SHORT_DELTA_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund

    regex = GREEKS_LONG_SHORT_DELTA_REGEX if regex is None else regex
    schema_overrides = GREEKS_LONG_SHORT_DELTA_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)

    return dataframe, md5, real_date


def volatility_analysis (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,
    ) :
    """
    Docstring for volatility_analysis
    """
    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund
    
    df_1, md5_1, real_date_1 = vega_stress_pnl(date, fund)
    df_2, md5_2, real_date_2 = vega_bucket(date, fund)

    return df_1, md5_1, real_date_1, df_2, md5_2, real_date_2

    
def vega_stress_pnl (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

        path_by_fund : Optional[Dict] = None,
        schema_overrides : Optional[Dict] = None,

        mode : str = "le"
    ) :
    """
    Docstring for vega_stress_pnl
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_VEGA_STRESS_PNL_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund
    regex = GREEKS_VEGA_STRESS_PNL_REGEX if regex is None else regex

    schema_overrides = GREEKS_VEGA_STRESS_PNL_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)
    dataframe = dataframe.filter(pl.col("Underlying") != "Total")

    return dataframe, md5, real_date


def vega_bucket (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,
        regex : Optional[re.Pattern] = None,

        path_by_fund : Optional[Dict] = None,
        schema_overrides : Optional[Dict] = None,

        mode : str = "le"
    
    ) :

    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_VEGA_BUCKET_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund
    regex = GREEKS_VEGA_BUCKET_REGEX if regex is None else regex

    schema_overrides = GREEKS_VEGA_BUCKET_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)
    dataframe = dataframe.filter(pl.col("Underlying Asset") != "Total")

    return dataframe, md5, real_date




def greeks_risk_analysis (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

    ) :
    """
    Docstring for greeks_risk_analysis
    """
    df_greeks, md5_greeks, greeks_date = greeks_risk(date, fund)
    df_credit, md5_credit, credit_date = risk_credit(date, fund)

    return df_greeks, greeks_date, md5_greeks, df_credit, credit_date, md5_credit




def greeks_risk (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None, 
        schema_overrides : Optional[Dict] = None,

        mode : str = "le"

    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_RISK_EQUITY if path_by_fund is None else path_by_fund

    regex = GREEKS_REGEX if regex is None else regex
    schema_overrides = GREEKS_RISKS_EQUITY_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)

    return dataframe, md5, real_date



def risk_credit (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None,

        filename : Optional[str] = None,

        regex : Optional[re.Pattern] = None,
        path_by_fund : Optional[str] = None, 
        schema_overrides : Optional[Dict] = None,

        mode : str = "le"

    ) :
    """
    
    """
    date = str_to_date(date)
    fund = FUND_HV if fund is None else fund

    path_by_fund = GREEKS_RISK_CREDIT_FUNDS_DIR_PATHS if path_by_fund is None else path_by_fund

    regex = GREEKS_RISK_CREDIT_REGEX if regex is None else regex
    schema_overrides = GREEKS_RISK_CREDIT_COLUMNS if schema_overrides is None else schema_overrides

    dataframe, md5, real_date = read_greeks_by_date(date, fund, None, path_by_fund, schema_overrides, regex, mode)

    return dataframe, md5, real_date


# Filter and compute functions


def filter_greeks_by_assets (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        column : Optional[str] = None,

        rules : Optional[Dict] = None,
        assets : Optional[List] = None,

    
    ) :
    """
    Docstring for filter_greeks_by_assets
    
    :param dataframe: Description
    :type dataframe: Optional[pl.DataFrame]
    """    
    if len(assets) == 0 :
        return dataframe, md5
    
    rules = GREEKS_ASSET_CLASS_RULES if rules is None else rules

    tokens: list[str] = []
    for a in assets:
        tokens.extend(rules.get(a, []))

    s = pl.col(column).cast(pl.Utf8, strict=False).fill_null("")
    cond = pl.any_horizontal([s.str.contains(t) for t in tokens])

    df = dataframe.filter(cond)

    return df, md5



def compute_gamma_pnl_sum (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        columns : Optional[List[str]] = None,

    ) :
    """
    
    """
    sums_df = pl.DataFrame(
        {
            "column": columns,
            "Sum" : [
                dataframe.select(pl.col(c).sum()).item()
                if c in dataframe.columns else None
                for c in columns
            ]
        }
    )

    return sums_df
