from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import random
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from email_validator import validate_email, EmailNotValidError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from base64 import urlsafe_b64encode
from flask import render_template, request
from App.encryption import decrypt, encrypt

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_credentials():
    
    try:
        with open("encrypted_token.txt", "rb") as token_file:
            encrypted_token = token_file.read()
            token_string = decrypt(encrypted_token)
    except Exception as e:
        print(e)
        return None
    
    credentials = None
    if token_string:
        token = json.loads(token_string)
        credentials = Credentials.from_authorized_user_info(token, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            with open("encrypted_token.txt", 'wb') as token_file:
                encrypted_token = encrypt(credentials.to_json())
                token_file.write(encrypted_token)
        else:
            return None
    return credentials

def get_gmail_service():
    credentials = get_credentials()
    if credentials is None:
        return None
    service = build('gmail', 'v1', credentials=credentials)
    return service

def send_email(email, subject, body):
    try:
        service = get_gmail_service()
        msg = MIMEMultipart()
        msg['To'] = email
        msg['From'] = 'me'
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        with open("App/static/images/PhytoGuard.jpg", "rb") as logo:
            image_binary = logo.read()
            image = MIMEImage(image_binary)
            image.add_header("Content-ID", "<logo>")
            image.add_header("Content-Disposition", "inline", filename="PhytoGuard.jpg")
            msg.attach(image)
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
    try:  
        body = render_template("verification.html", passcode=passcode)
        send_email(email, "Email Verification", body)
        return passcode 
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def create_new_token(token):
    try:
        with open("encrypted_token.txt", "wb") as token_file:
            token_file.write(token.encode('utf-8'))
            print(decrypt(token.encode("utf-8")))
            return True
    except Exception as e:
        print(e)
        return False