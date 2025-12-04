import os, re
import polars as pl
import datetime as dt

import win32com.client as win32
import pythoncom as pycom

from typing import Dict, List, Optional
from email.message import EmailMessage

from src.utils.formatters import check_email_format
from src.config.parameters import EMAIL_DEFAULT_TO, EMAIL_DEFAULT_CC, EMAIL_DEFAULT_FROM, PAYMENTS_EMAIL_SUBJECT, PAYMENTS_EMAIL_BODY
from src.config.paths import MESSAGE_SAVE_DIRECTORY


def create_email_item (
        
        to_email : Optional[str | List[str]] = None,
        cc_email : Optional[str | List[str]] = None,
        from_email : Optional[str] = None,

        subject : Optional[str] = None,
        body : Optional[str] = None,

        content_file_paths : Optional[str | List[str]] = None
        
    ) -> win32.Dispatch :
    """
    This function sends an email using Outlook.
    
    Args:
        to_email (List[str]): List of recipient email addresses. If None or empty, defaults to DEFAULT_TO_EMAIL.
        cc_email (List[str]): List of CC email addresses. If None or empty, defaults to DEFAULT_CC_EMAIL.
        from_email (str): Sender email address to appear in 'From' (SendOnBehalfOfName).
        subject (str): Subject of the email.
        body (str): Body content in HTML.
        content_file_paths (List[str], optional): List of file paths to attach to the email.

    Returns:
        mail_item (win32.Dispatch) : The generated Outlook email item.
    """
    from_email = EMAIL_DEFAULT_FROM if from_email is None else from_email

    if from_email == "" :
        return None

    to_email = [EMAIL_DEFAULT_FROM] if to_email is None else (
        [to_email] if isinstance(to_email, str) else to_email
    )

    if len(to_email) == 0 :
        return None

    cc_email = [EMAIL_DEFAULT_CC] if cc_email is None else (
        [cc_email] if isinstance(cc_email, str) else cc_email
    )

    content_file_paths = [content_file_paths] if isinstance(content_file_paths, str) else content_file_paths 
    
    subject = PAYMENTS_EMAIL_SUBJECT if subject is None else subject
    body = PAYMENTS_EMAIL_BODY if body is None else body

    email_item = EmailMessage()
    email_item["From"] = from_email
    
    # Set up recipents and CCs (Assumens that email are in ccorect form)
    email_item["To"] = ", ".join(to_email)

    if cc_email and len(cc_email) > 0 :
        email_item["Cc"] = ", ".join(cc_email)
    
    email_item["Subject"] = subject
    
    # Version HTML : on remplace les \n par <br>
    html_body = body.replace("\n", "<br>")

    email_item.set_content("This email requires an HTML-capable client.")
    email_item.add_alternative(html_body, subtype="html")
    
    email_item["X-Unsent"] = "1"
    
    if content_file_paths is not None :

        for attachment in content_file_paths :
            
            if not os.path.isfile(attachment) :
                continue

            with open(attachment, "rb") as f :  
                data = f.read()

            basename = os.path.basename(attachment)

            email_item.add_attachment(

                data,
                maintype="application",
                subtype="octet-stream",
                filename=basename

            )

    return email_item


def save_email_item (
        
        email_item : Optional[EmailMessage] = None,
        filename : Optional[str] = None,
        abs_path_dir : Optional[str] = None
        
    ) -> Optional[Dict] :
    """
    Saves an email item and returns the result status.

    Args:
        email_data (dict): The email data to save.

    Returns:
        dict: Contains:
            - 'success' (bool): True if save succeeded, False otherwise.
            - 'message' (str): A message describing the result.
            - 'path' (str) : The path of the saved file.
    """
    os.makedirs(abs_path_dir, exist_ok=True)

    if filename is None :

        timestamped = generate_timestamped_name()
        filename = f"message_{timestamped}.eml"

    abs_path_dir = MESSAGE_SAVE_DIRECTORY if abs_path_dir is None else abs_path_dir
    save_path = os.path.join(abs_path_dir, filename)
    
    status = {

        "success" : False,
        "message" : "",
        "path" : ""

    }

    try :

        with open(save_path, "wb") as f :
            f.write(bytes(email_item))

        status["success"] = True
        status["message"] = "Email saved successfully"
        status["path"] = save_path

    except Exception as e :

        status["message"] = f"Failed to save email: {str(e)}"
        return status

    return status


def generate_timestamped_name () -> str :
    """
    Generates a unique timestamped string based on the current date and time.

    Returns:
        str: A string formatted as 'YYYYMMDD_HHMMSS_microseconds', 
             e.g., '20250801_143255_123456'.
    """
    name = dt.datetime.now().strftime(format="%Y%m%d_%H%M%S_%f")

    return name
