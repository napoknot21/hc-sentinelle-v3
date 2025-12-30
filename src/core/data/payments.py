from __future__ import annotations

import os
import time
import polars as pl
import datetime as dt

from typing import Optional, Dict, List

from src.config.parameters import (
    PAYMENTS_COLUMNS, SECURITIES_COLUMNS, PAYMENTS_BENEFICIARY_COLUMNS, PAYMENTS_BENECIFIARY_SHEET_NAME,
    PAYMENTS_EMAIL_FROM, PAYMENTS_EMAIL_CCs, PAYMENTS_EMAIL_SUBJECT, PAYMENTS_EMAIL_TO, PAYMENTS_EMAIL_BODY
)
from src.config.paths import (
    PAYMENTS_DB_ABS_PATH, PAYMENTS_DB_REL_PATH,
    SECURITIES_DB_REL_PATH, PAYMENTS_BENECIFIARY_DB_ABS_PATH, PAYMENTS_FILES_ABS_PATH,
    PAYMENTS_MESSAGES_DIR_ABS_PATH
)
from src.utils.data_io import load_excel_to_dataframe, convert_payement_to_excel, export_excel_to_pdf
from src.utils.logger import log
from src.utils.outlook import create_email_item, save_email_item


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

        columns : Optional[Dict] = None,

    ) :
    """
    
    """
    dataframe, _ = load_beneficiaries_db() if dataframe is None else (dataframe, md5)
    columns = PAYMENTS_BENEFICIARY_COLUMNS if columns is None else columns

    specific_cols = list(columns.keys())[:3]

    if counterparty is None or type_ben is None or currency is None :
        return None

    df_match = (

        dataframe
        .filter(

            (pl.col(specific_cols[0]).str.strip_chars() == counterparty.strip()) &
            (pl.col(specific_cols[1]).str.strip_chars() == type_ben.strip()) &
            (pl.col(specific_cols[2]).str.strip_chars() == currency.strip())

        )

    )

    if df_match.is_empty() :
        return None

    row = df_match.row(0)

    benef_bank  = row[3]
    swift_code  = row[4]
    swift_ben   = row[5] if row[5] is not None else "Nan"
    iban        = row[6]

    return swift_code, benef_bank, swift_ben, iban


def process_payments_to_excel (
        
        payments : Optional[List] = None,
        dir_abs_path : Optional[str] = None

    ) :

    """
    
    """
    if payments is None or len(payments) == 0 :
    
        log("No payement information to convert", "error")
        return False
    
    dir_abs_path = PAYMENTS_FILES_ABS_PATH if dir_abs_path is None else dir_abs_path
    filepaths = []
    
    for payment in payments :
        
        try :

            fileout = convert_payement_to_excel(payment, dir_abs_path=dir_abs_path)
            filepaths.append(fileout)

            time.sleep(1) # this line allows to get different name files

        except :
            
            print("Error during conversion")

    if len(filepaths) == 0 :

        log("[-] No Payment to convert to PDF", "error")
        return None
    
    return filepaths


def process_excel_to_pdf (
        
        filepaths : Optional[List] = None,
        dir_abs_path : Optional[str] = None,
    
    ) :
    """
    Docstring for process_excel_to_pdf
    
    :param filepaths: Description
    :type filepaths: Optional[List]
    :param dir_abs_path: Description
    :type dir_abs_path: Optional[str]
    """
    if filepaths is None or len(filepaths) == 0 :
        return None
    
    dir_abs_path = PAYMENTS_FILES_ABS_PATH if dir_abs_path is None else dir_abs_path
    pdf_filespaths = []

    for filepath in filepaths :

        try :
            
            filename = os.path.splitext(os.path.basename(filepath))[0]
            dict = export_excel_to_pdf(filepath, filename + ".pdf", dir_abs_path)

            pdf_filespaths.append(dict.get("path"))

        except :
            log("[-] Error during excel to PDF conversion", "error")

    return pdf_filespaths


def create_payement_email (
        
        from_email : Optional[str] = None,
        to_email: Optional[str] = None,
        cc_email : Optional[str] = None,

        subject_email : Optional[str] = None,
        body_email : Optional[str] = None,

        files_attached : Optional[List] = None,
        save_msg_abs : Optional[str] = None,

    ) :
    """
    Docstring for create_payement_email
    
    :param from_email: Description
    :type from_email: Optional[str]
    :param to_email: Description
    :type to_email: Optional[str]
    :param cc_email: Description
    :type cc_email: Optional[str]
    :param subject_email: Description
    :type subject_email: Optional[str]
    :param body_email: Description
    :type body_email: Optional[str]
    :param files_attached: Description
    :type files_attached: Optional[List]
    """
    from_email = PAYMENTS_EMAIL_FROM if from_email is None else from_email
    to_email = PAYMENTS_EMAIL_TO if to_email is None else to_email
    cc_email = PAYMENTS_EMAIL_CCs if cc_email is None else cc_email

    subject_email = PAYMENTS_EMAIL_SUBJECT if subject_email else subject_email
    body_email = PAYMENTS_EMAIL_BODY if body_email is None else body_email
    
    save_msg_abs = PAYMENTS_MESSAGES_DIR_ABS_PATH if save_msg_abs is None else save_msg_abs

    email = create_email_item(to_email, cc_email, from_email, subject_email, body_email, files_attached)
    
    timestamped = dt.datetime.now().strftime(format="%Y%m%d_%H%M%S_%f")
    filename = f"message_{timestamped}.eml"

    status = save_email_item(email, filename, save_msg_abs)

    return status

