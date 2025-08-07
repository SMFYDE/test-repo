import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']

message = "Subject: Test Email\n\nYes im a simp"

with smtplib.SMTP("smtp-mail.outlook.com", 587) as s:
    s.set_debuglevel(1)
    s.starttls()
    s.login(EMAIL_USER, EMAIL_PASS)
    s.sendmail(EMAIL_USER, "yannis.defontaine@socotec.com", message)
