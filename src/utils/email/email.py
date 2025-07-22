import os
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


def create_email_item (to_email=[], cc_email=[], from_email="", subject="", body="", content_file_paths="") :
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
        - 
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
    mail_item.body = generate_html_body(body)

    # Attach files to the email
    for file_path in content_file_paths :
        mail_item.Attachments.Add(Source=file_path)

    # Save the mail into the directory
    save_message_path = MESSAGE_SAVE_DIRECTORY + generate_timestamped_name() + ".msg"
    mail_item.SaveAs(save_message_path, 3)

    return save_message_path
    

def generate_html_body (body: str) :
    """
    This function returns a pre defined HTML body
    """
    html_body = f"""<p>{body}</p><p class="MsoNormal"><o:p> </o:p></p><p class="MsoNormal"><span lang="FR" style="mso-ansi-language:FR">Best regards,<o:p></o:p></span></p><p class="MsoNormal"><b><span lang="EN-US" style="font-size:14.0pt;font-family: 'helvetica light';color:#0d1b7b;mso-ansi-language:en-us;mso-fareast-language: en-gb;">Trading Desk</span></b><span lang="EN-GB" style="color:#0D1B7B;mso-ansi-language: EN-GB;mso-fareast-language:EN-GB"><o:p></o:p></span></p><p class="MsoNormal"><span lang="EN-US" style="font-size:10.5pt;font-family:'helvetica light';color:#272727;mso-ansi-language:en-us;mso-fareast-language:en-gb;"> </span><span lang="EN-GB" style="mso-ascii-font-family:Calibri;mso-ascii-theme-font:minor-latin; mso-hansi-font-family:Calibri;mso-hansi-theme-font:minor-latin;color:black; mso-ansi-language:EN-GB;mso-fareast-language:EN-GB"><o:p></o:p></span></p><p class="MsoNormal"><span lang="EN-US" style="font-size:10.0pt;font-family:'helvetica light';color:#0d1b7b;mso-ansi-language:en-us;mso-fareast-language:en-gb;">t: </span><span lang="EN-US" style="font-size:10.0pt;font-family:'helvetica light';color:#595959; mso-ansi-language:en-us;mso-fareast-language:en-gb;">+356 277 421 15</span><span lang="EN-GB" style="color:black;mso-ansi-language:EN-GB;mso-fareast-language: EN-GB"><o:p></o:p></span></p><p class="MsoNormal"><span lang="EN-US" style="font-size:10.0pt;font-family:'helvetica light';color:#0d1b7b;mso-ansi-language:en-us;mso-fareast-language:en-gb;">a: </span><span lang="EN-US" style="font-size:10.0pt;font-family:'helvetica light';color:#595959; mso-ansi-language:en-us;mso-fareast-language:en-gb;">Altarius Asset Management Ltd</span><span lang="EN-GB" style="color:#595959;mso-ansi-language:EN-GB; mso-fareast-language:EN-GB"><o:p></o:p></span></p><p class="MsoNormal"><span lang="EN-US" style="font-size:10.0pt;font-family:'helvetica light';color:#595959;mso-ansi-language:en-us;mso-fareast-language:en-gb;"> Cornerstone Complex, Suite A, Level 1, 16th September Square, Mosta MST 1180 Malta</span><span lang="EN-GB" style="color:#595959;mso-ansi-language:EN-GB; mso-fareast-language:EN-GB"><o:p></o:p></span></p><p class="MsoNormal"><span lang="EN-GB" style="font-size:10.0pt;font-family:'helvetica light';color:#0d1b7b;mso-ansi-language:en-gb;mso-fareast-language:en-gb;">w: </span><u><span lang="EN-GB" style="font-size:10.0pt;font-family:'helvetica light';color:#244171; border:none windowtext 1.0pt;mso-border-alt:none 0cm;padding:0cm; mso-ansi-language:en-gb;mso-fareast-language:en-gb;"><a href="http://www.altariusam.com/" title="http://www.altariusam.com/"><span style="color:#244171">www.altariusam.com</span></a></span></u><span lang="EN-GB" style="font-size:10.0pt;font-family:'helvetica light';color:#272727;mso-ansi-language: en-gb;mso-fareast-language:en-gb;"> </span><span lang="EN-GB" style="font-size:10.0pt;font-family:'helvetica light';color:#0d1b7b;border: none windowtext 1.0pt;mso-border-alt:none 0cm;padding:0cm; mso-ansi-language:en-gb;mso-fareast-language:en-gb;">e: </span><u><span lang="EN-GB" style="font-size:10.0pt;font-family:'helvetica light';color:#244171; border:none windowtext 1.0pt;mso-border-alt:none 0cm;padding:0cm; mso-ansi-language:en-gb;mso-fareast-language:en-gb;"><a href="mailto:tradingdesk@altariusam.com">tradingdesk@altariusam.com</a></span></u></p>"""

    return html_body


def generate_timestamped_name () :
    """
    Generates a timestamped name using the current time and date
    """
    name = dt.datetime.now().strftime(format="¨%Y%m%d_%H%M%S_%f")

    return name