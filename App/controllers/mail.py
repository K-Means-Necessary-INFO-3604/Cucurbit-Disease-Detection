from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import random
import json
from email_validator import validate_email, EmailNotValidError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode
from flask import render_template

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_credentials():
    
    token_string = os.environ.get("TOKEN")
    credentials = None
    if token_string:
        token = json.loads(token_string)
        credentials = Credentials.from_authorized_user_info(token, SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            with open(".env", 'w') as env:
                env.write(f"TOKEN={credentials.to_json()}")
        else:
            return None
    return credentials

def get_gmail_service():
    credentials = get_credentials()
    if credentials is None:
        return None
    service = build('gmail', 'v1', credentials=credentials)
    return service

def send_email(service, email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['To'] = email
        msg['From'] = 'me'
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        raw_message = urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def validate_email_syntax(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        return False


def send_verification(email):
    passcode = random.randrange(100000, 999999)
    body = render_template("verification.html", passcode=passcode)
    
    try:
        service = get_gmail_service()
        send_email(service, email, "Email Verification", body)
        return passcode 
    except Exception as e:
        print(f"An error occurred: {e}")
        return None