import os, re
import polars as pl
import datetime as dt

import win32com.client as win32
import pythoncom as pycom

from src.config.parameters import DEFAULT_TO_EMAIL, DEFAULT_CC_EMAIL, DEFAULT_FROM_EMAIL
from src.config.paths import MESSAGE_SAVE_DIRECTORY


def create_email_item (
        to_email : list = None,
        cc_email : str = None,
        from_email : str = DEFAULT_FROM_EMAIL,
        subject : str = "",
        body : str = "",
        content_file_paths : list = None
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


    # Create the Outlook application object
    pycom.CoInitialize()
    outlook_app = win32.Dispatch('Outlook.Application')

    # Create a new mail item
    mail_item = outlook_app.CreateItem(0)

    # Set up recipeients and CCs (Assumes that emails are in correct format)
    mail_item.To = DEFAULT_TO_EMAIL if (len(to_email) == 0 or to_email is None) else "; ".join(to_email)
    mail_item.CC = DEFAULT_CC_EMAIL if (len(cc_email) == 0 or cc_email is None) else "; ".join(cc_email)

    # Set up sender email
    mail_item.SendOnBehalfOfName = DEFAULT_FROM_EMAIL if from_email == "" else from_email

    # Set up of subject email
    mail_item.Subject = subject

    # Body set up for the email
    mail_item.HTMLBody = generate_html_template_body(body)

    # Attach files to the email
    for file_path in content_file_paths :
        
        if os.path.isfile(file_path) :
            mail_item.Attachments.Add(Source=file_path)

        else :
            print("\n[-] File not found. Not attached...\n")


    return mail_item


def save_email_item (email_item : win32.Dispatch, abs_path_directory : str = MESSAGE_SAVE_DIRECTORY) -> dict :
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
    timestamped = generate_timestamped_name()
    file_name = f"message_{timestamped}.msg"

    save_dir = abs_path_directory if os.path.isdir(abs_path_directory) else MESSAGE_SAVE_DIRECTORY
    save_path = os.path.join(save_dir, file_name)
    
    status = {

        "success" : False,
        "message" : "",
        "path" : ""

    }

    try :

        email_item.SaveAs(save_path, 3)

        status["success"] = True
        status["message"] = "Email saved successfully"
        status["path"] = save_path

    except Exception as e :

        status["message"] = f"Failed to save email: {str(e)}"
        return status

    return status


def send_email (email_item ! win32.Dispatch) -> bool :
    """
    Sends the given Outlook mail item immediately via Outlook.

    Args:
        mail_item (win32.Dispatch): The Outlook MailItem object to send.

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Raises:
        None: Exceptions are caught internally; failures result in False return value.

    Notes:
        - This function requires Outlook to be installed and properly configured on the system.
        - Ensure the mail_item has all required fields set (To, Subject, Body) before calling.
        - Sending emails programmatically may trigger Outlook security prompts depending on security settings.
    """
    try :

        email_item.Send()
        return True
    
    except Exception as e :

        print(f"[-] Failed to send email: {e}")
        return False


def generate_html_template_body (body: str) -> str:
    """
    Creates a standard HTML email body by embedding the provided content 
    and appending a fixed company signature.

    Args:
        body (str): The main content of the email in plain text or HTML.

    Returns:
        str: A complete HTML string with the body content wrapped in <p> tags 
             followed by the company signature.
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