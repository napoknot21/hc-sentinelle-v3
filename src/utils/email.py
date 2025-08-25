import os
import re

import requests
import base64
import json

import polars as pl
import datetime as dt

from typing import Dict, Optional, List, Any

from src.config.parameters import (
    CLIENT_ID, CLIENT_SECRET_VALUE, TENANT_ID, EMAIL_URL_GET_TOKEN, EMAIL_URL_SEND_MAIL,
    DEFAULT_TO_EMAIL, DEFAULT_CC_EMAIL, DEFAULT_FROM_EMAIL
)
from src.config.paths import MESSAGE_SAVE_DIRECTORY
from src.utils.formatters import check_email_format


def get_token_azure (
    
        client_id : str = CLIENT_ID,
        client_secret_value : str = CLIENT_SECRET_VALUE,
        tenant_id : str = TENANT_ID,
        url : str = EMAIL_URL_GET_TOKEN
    
    ) -> Optional[str] :
    """
    
    """
    url = url.replace("TENANT_ID", tenant_id)

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
        
        token : str | None = None,
        from_email : str = DEFAULT_FROM_EMAIL,
        cc_email : List[str] = None,
        to_email : List[str] | None = None,
        subject : str = "",
        content : str = "",
        file_abs_path : str | None = None,
        endpoint : str = EMAIL_URL_SEND_MAIL,

    ) -> bool :
    """
    
    """
    token = get_token_azure() if token is None else token
    endpoint = endpoint.replace("SENDER_MAIL", from_email)
    to_email = [DEFAULT_TO_EMAIL] if to_email is None else to_email
    cc_email = [DEFAULT_CC_EMAIL] if cc_email is None else cc_email

    headers = {

        "Authorization" : f"Bearer {token}",
        "Content-Type" : "application/json"

    }

    body = {

        "contentType" : "text",
        "content" : content

    }

    recipients = []
    for email in to_email :

        if check_email_format(email) :
                
            recipients.append(
                {
                    "emailAddress": { "address": email }
                }
            )

    cc_recipients = []
    for email in cc_email :

        if check_email_format(email) :
                
            cc_recipients.append(
                {
                    "emailAddress": { "address": email }
                }
            )

    message = {

        "subject" : subject,
        "body" : body,
        "toRecipients" : recipients

    }

    # Add ccRecipients if any valid emails found
    if cc_recipients :
        message["ccRecipients"] = cc_recipients

    payload = {

        "message" : message,
        "saveToSentItems" : "true"

    }

    if file_abs_path is not None :

        if os.path.exists(file_abs_path) :

            base_name = os.path.basename(file_abs_path)
            bytes_file = convert_bytes_64(file_abs_path)

            attachment = [
                {
                    "@odata.type" : "#microsoft.graph.fileAttachment",
                    "name" : base_name,
                    "contentType" : "text/plain",
                    "contentBytes" : bytes_file,
                }
            ]

            payload["message"]["attachments"] = attachment

        else :
            print("[-] File attached does not exist. Sending without attachment")

    try :

        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        print(response.text)
    
    except Exception as e :
        
        print("[-] error while sending email")
        return False
    
    print("[+] Email send.")

    return True


def convert_bytes_64 (file_abs_path : str) :
    """
    
    """
    # We assume the path is not None and exists
    with open(file_abs_path, "rb") as f :
        base64_cont = base64.b64encode(f.read()).decode('utf-8')

    return base64_cont


def generate_timestamped_name () -> str :
    """
    Generates a unique timestamped string based on the current date and time.

    Returns:
        str: A string formatted as 'YYYYMMDD_HHMMSS_microseconds', 
             e.g., '20250801_143255_123456'.
    """
    name = dt.datetime.now().strftime(format="%Y%m%d_%H%M%S_%f")

    return name


