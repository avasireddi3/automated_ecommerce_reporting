import smtplib
import os
import mimetypes
from email.message import EmailMessage
from credentials import gmail_user,gmail_password

EMAIL_ADDRESS = gmail_user
EMAIL_PASSWORD = gmail_password

msg = EmailMessage()
msg['Subject'] = 'Daily report'
msg['From'] = EMAIL_ADDRESS
msg['To'] = "avasireddi3@gmail.com"
msg.set_content('Please find attached the report')
filepath="test.csv"
with open(filepath,"rb") as f:
    file_data =  f.read()
    file_type =  "csv"

ctype, encoding = mimetypes.guess_type(filepath)
if ctype is None or encoding is not None:
    # No guess could be made, or the file is encoded (compressed), so
    # use a generic bag-of-bits type.
    ctype = 'application/octet-stream'
maintype, subtype = ctype.split('/', 1)
msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename = 'test.csv')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

