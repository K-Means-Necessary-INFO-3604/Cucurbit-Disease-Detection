from App.config import get_mail
from flask import render_template
from flask_mail import Message
import os
from email_validator import validate_email, EmailNotValidError
import random



def validate_email_syntax(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        return False

def send_verification(email):
    message = Message(subject="PhytoGuard Email Verification", recipients=[email], sender="noreply@yahoo.com")
    image_path = os.path.join("App", "static", "images", "PhytoGuard.jpg")
    passcode = random.randrange(100000, 999999)
    with open(image_path, "rb") as file:
        image = file.read()
        message.attach(filename="PhytoGuard.jpg", content_type="image/jpeg", data=image, disposition="inline",  headers={'Content-ID': '<logo>'})
        message.html = render_template("verification.html", passcode=passcode)
    try:
        mail = get_mail()
        mail.send(message)
        return passcode
    except Exception as e:
        return None