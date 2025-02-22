from App.models import Upload
from App.database import db
import cv2
import base64
from datetime import datetime
import pytz

allowed = {'jpg', 'jpeg', 'png'}

def upload_image(image, user_id):
    ast = pytz.timezone("America/Port_of_Spain")
    date = datetime.now(ast)
    upload = Upload(image=image, date=date.date(), user_id=user_id)
    db.session.add(upload)
    db.session.commit()
    return upload

def upload_guest(image):
    date = datetime.utcnow()
    upload = Upload(image=image, date=date)
    return upload

def get_upload(id):
    upload = Upload.query.get(id)
    if upload:
        return upload
    return None

def get_all_uploads():
    uploads = Upload.query.all()
    return uploads

def get_uploads_by_date(user_id):
    uploads = Upload.query.filter_by(user_id=user_id).order_by(Upload.date.desc()).all()
    return uploads

def get_all_uploads_json():
    uploads = Upload.query.all()
    if not uploads:
        return []
    uploads_json = [upload.get_json() for upload in uploads]
    return uploads_json

def validate_upload(filename):
    if filename == '':
        return None
    if '.' not in filename:
        return None
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in allowed:
        return None
    return filename

def encode_image(image):
    encoded_img = base64.b64encode(image).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded_img}"