import os, re
import pandas as pd
import datetime as dt

import win32com.client as win32
import pythoncom as pycom

from dotenv import load_dotenv

# Default global variables load and get
load_dotenv()

DEFAULT_TO_EMAIL=os.getenv('DEFAULT_TO_EMAIL')
DEFAULT_CC_EMAIL=os.getenv('DEFAULT_CC_EMAIL')
DEFAULT_FROM_EMAIL=os.getenv('DEFAULT_FROM_EMAIL')
MESSAGE_SAVE_DIRECTORY=os.getenv('MESSAGE_SAVE_DIRECTORY')


def create_email_item (to_email=[], cc_email=[], from_email="", subject="", body="", content_file_paths=[]) :
    """
    This function sends an email using Outlook.
    
    Args :
        - to_email              : List (str)    -> Email addresses of the recipients.
        - cc_email              : List (str)    -> Email addresses for CCs.
        - from_email            : Str           -> Sender's email address. 
        - subject               : Str           -> Email's subject.
        - body                  : Str           -> Body's text of the email.
        - content_file_paths    : List (str)    -> Path's list file to be attached.

    Returns :
        - mail_item : Dispatch object -> The generated Outlook email item.
    """
    # Create the Outlook application object
    pycom.CoInitialize()
    outlook_app = win32.Dispatch('Outlook.Application')

    # Create a new mail item
    mail_item = outlook_app.CreateItem(0)

    # Set up recipeients and CCs
    mail_item.To = DEFAULT_TO_EMAIL if len(to_email) == 0 else "; ".join(to_email)
    mail_item.CC = DEFAULT_CC_EMAIL if len(cc_email) == 0 else "; ".join(cc_email)

    # Set up sender email
    mail_item.SendOnBehalfOfName = DEFAULT_FROM_EMAIL if from_email == "" else from_email

    # Set up of subject email
    mail_item.Subject = subject

    # Body set up for the email
    mail_item.HTMLBody = generate_html_body(body)

    # Attach files to the email
    for file_path in content_file_paths :
        mail_item.Attachments.Add(Source=file_path)

    return mail_item


def save_email_item (email_item, path : str) -> str :
    """
    Saves the email item in a given directory from a Outlook item
    """
    timestamped = generate_timestamped_name()
    file_name = f"message_{timestamped}.msg"

    save_dir = MESSAGE_SAVE_DIRECTORY if path is None else path
    save_path = os.path.join(save_dir, file_name)
    
    email_item.SaveAs(save_path, 3)

    return save_path


def generate_html_body(body: str) -> str:
    """
    Returns a standard HTML body with signature appended.
    """
    html_body = f"""<p>{body}</p>
    <p>Best regards,</p>
    <p><strong>Trading Desk</strong><br>
    Altarius Asset Management Ltd<br>
    Cornerstone Complex, Suite A, Level 1,<br>
    16th September Square, Mosta MST 1180 Malta<br>
    t: +356 277 421 15<br>
    <a href="http://www.altariusam.com/">www.altariusam.com</a><br>
    <a href="mailto:tradingdesk@altariusam.com">tradingdesk@altariusam.com</a></p>
    """

    return html_body


def generate_timestamped_name () -> str :
    """
    Generates a timestamped name using the current time and date
    """
    name = dt.datetime.now().strftime(format="%Y%m%d_%H%M%S_%f")

    return name


def check_email_format (email : str) -> bool :
    """
    Returns True if the email address has a valid format, otherwise False.
    """
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

    return re.match(email_regex, email) is not None