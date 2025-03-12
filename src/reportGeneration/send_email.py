import smtplib
import mimetypes
from email.message import EmailMessage
from src.config import pdf_name, xlsx_file_name, msg_content,to
from src.credentials import gmail_user,gmail_password

EMAIL_ADDRESS = gmail_user
EMAIL_PASSWORD = gmail_password

def send_mail()->None:
    msg = EmailMessage()
    msg['Subject'] = "Daily Ecommerce Report Test"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    msg.set_content(msg_content)
    filepaths=[f"demo_files/{xlsx_file_name}.xlsx",f"demo_files/{pdf_name}.pdf"]
    for filepath in filepaths:
        with open(filepath,"rb") as f:
            file_data =  f.read()
        ctype, encoding = mimetypes.guess_type(filepath)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(file_data,
                           maintype=maintype,
                           subtype=subtype,
                           filename=filepath.split("/")[1])

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

