#!/usr/bin/env python3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from config import DATE_LAST_HOUR, LAST_HOUR, SENDER, subject
from data.db import yamld
import csv
import time

import visualizations as vz

html, eod_projection = vz.create_email_html()

def recipients(test=False):
    if test is False:
        recipients_lst = list()
        with open(yamld['recipients'], 'rU') as f:
            reader = csv.reader(f)
            return list(reader)
    else:
        return [['fpombeiro@fandango.com'],
                ['BIENG@fandango.com'],
                ['RMookherjee@fandango.com']]
 
def smtp_mailer():
    recipients_lst = [x[0] for x in recipients(test=yamld['testing'])]
    print(subject(eod_projection))
    html_email = "<!DOCTYPE html><html><head><title>Hourly Report</title></head><body>"
    html_email += str(html) + "</body></html>"
    message = MIMEText(html_email, 'html', 'utf-8')
    message['from'] = SENDER
    message['to'] = ",".join(recipients_lst)
    message['subject'] = subject(eod_projection)
    try:
        smtpObj = smtplib.SMTP('localhost') #"smtp.gmail.com:587"
        smtpObj.sendmail(SENDER, recipients_lst, message.as_string())
        print("Mail Successfully Sent!")
    except Exception as e:
        print("Failed to send mail due to ", e)

