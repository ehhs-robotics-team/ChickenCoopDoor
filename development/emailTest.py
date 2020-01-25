#!/usr/bin/python3
import smtplib
import traceback
from astral import Location
import time
from context import settings

gmail_user = settings.gmail_user  
gmail_password = settings.gmail_password

sent_from = gmail_user  
to = ['ehhsnerdz@gmail.com']  
subject = 'Python auto email testing'  
body = 'Testing the email function:'

email_text = '''\
From: {0}
To: {1}
Subject: {2}

{3}

'''.format(sent_from, ", ".join(to), subject, body)

def writeToFile(data):
    with open("/home/pi/Desktop/test.log", "a") as datalog:
        datalog.write(data +"\n")

try:  
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    print('Email sent!')
except Exception as e:  
    print('Something went wrong...')
    print(e)

print("ctrl+c to exit")

while 1:
    time.sleep(1)
    print(".", end="",flush=True)
    
