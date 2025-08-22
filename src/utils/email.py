import os
import re

import requests
import base64
import json

import polars as pl
import datetime as dt

from typing import Dict, Optional, List, Any

from src.config.parameters import (
    CLIENT_ID,
    CLIENT_SECRET_VALUE,
    TENANT_ID,
    URL_AUTH_TOKEN,

    DEFAULT_TO_EMAIL,
    DEFAULT_CC_EMAIL,
    DEFAULT_FROM_EMAIL

)
from src.config.paths import MESSAGE_SAVE_DIRECTORY



def get_token_azure (
    
        client_id : str = CLIENT_ID,
        client_secret_value : str = CLIENT_SECRET_VALUE,
        tenant_id : str = TENANT_ID,
        url : str = URL_AUTH_TOKEN
    
    ) -> Optional[str] :
    """
    
    """
    url = url.replace("tenant_id", tenant_id)

    payload = {

        "client_id" : client_id,
        "client_secret" : client_secret_value,

    }

    try :

        response = requests.post(url=url, data=payload)
        print("[+] POST request for token successfull")

    except Exception as e :

        print("[-] Error during requestin the Azure token.")
        return None
    
    
    token = response.get("token")

    if token is None :

        print("[-] Error during Azure token extraction")

    else :

        print("[*] Token extraction successfully.")

    return token


def send_mail (
        
        token : str = None,
        from_email : str = DEFAULT_FROM_EMAIL,
        cc_email : str = DEFAULT_CC_EMAIL,
        to_email : List[str] = [DEFAULT_TO_EMAIL],
        file_abs_path : str = None

    ) -> bool :
    """
    
    """
    for email in to_email :

        if not check_email_format(email=email) :
            
            print(f"[-] Error: {email} does not respect email standart format. No email sent")
            return False

    token = token if token is not None else get_token_azure()


    payload = {


    }

    url = ""

    response = requests.post(url=url, data=payload)


    return True if response is not None else False








def generate_timestamped_name () -> str :
    """
    Generates a unique timestamped string based on the current date and time.

    Returns:
        str: A string formatted as 'YYYYMMDD_HHMMSS_microseconds', 
             e.g., '20250801_143255_123456'.
    """
    name = dt.datetime.now().strftime(format="%Y%m%d_%H%M%S_%f")

    return name


def check_email_format (email : str) -> bool :
    """
    Validates the format of an email address using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email matches the expected format, False otherwise.

    Note:
        This validation checks for a general pattern like 'user@domain.tld' 
        but does not guarantee that the email address actually exists.
    """
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

    return re.match(email_regex, email) is not None