import cv2
import base64

allowed = {'jpg', 'jpeg', 'png'}

def validate_upload(filename):
    if filename == '':
        return None
    if '.' not in filename:
        return None
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in allowed:
        return None
    return filename

def encode_image(filepath):
    img = cv2.imread(filepath)
    status, buffer = cv2.imencode(".jpg", img)
    encoded_img = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded_img}"