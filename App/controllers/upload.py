from App.models import Upload 
from App.database import db 
import cv2 
import base64 
from datetime import datetime 
import pytz 
import numpy as np 
from math import ceil 

allowed = {'jpg', 'jpeg', 'png'} 

def upload_image(image, user_id): 
    ast = pytz.timezone("America/Port_of_Spain") 
    date = datetime.now(ast) 
    severity = calculate_severity(image) 
    upload = Upload(image=image, date=date.date(), severity=severity, user_id=user_id) 
    db.session.add(upload) 
    db.session.commit() 
    return upload 

def upload_guest(image): 
    ast = pytz.timezone("America/Port_of_Spain") 
    date = datetime.now(ast) 
    severity = calculate_severity(image) 
    upload = Upload(image=image, date=date, severity=severity)  
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

def calculate_severity(binary_data): 
    nparr = np.frombuffer(binary_data, np.uint8) 
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
    if image is None: 
        print(f"Image not found") 
    else: 
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   
        image_resized = cv2.resize(image_rgb, (300, 300))   
        hsv = cv2.cvtColor(image_resized, cv2.COLOR_RGB2HSV)
        
        lower_shadow = np.array([0, 0, 0]) 
        upper_shadow = np.array([180, 255, 100]) 
        shadow_mask = cv2.inRange(hsv, lower_shadow, upper_shadow)  
        image_no_shadow = cv2.bitwise_and(image_resized, image_resized, mask=~shadow_mask) 
        
        lower_yellow = np.array([15, 100, 50]) 
        upper_yellow = np.array([35, 255, 255]) 
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)   
        lower_brown = np.array([2, 3, 10]) 
        upper_brown = np.array([38, 255, 200]) 
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)   
        diseased_mask = cv2.bitwise_or(yellow_mask, brown_mask)   
        kernel = np.ones((3, 3), np.uint8) 
        diseased_mask_expanded = cv2.dilate(diseased_mask, kernel, iterations=1) 
        
        lower_green = np.array([40, 100, 50]) 
        upper_green = np.array([70, 255, 255]) 
        green_mask = cv2.inRange(hsv, lower_green, upper_green)  
        green_near_disease = cv2.bitwise_and(green_mask, diseased_mask_expanded) 
        
        diseased_mask = cv2.bitwise_or(diseased_mask, green_near_disease) 
        diseased_only = np.zeros_like(image_resized) 
        diseased_only[diseased_mask != 0] = image_resized[diseased_mask != 0] 
        
        diseased_pixels = np.count_nonzero(np.all(diseased_only != 0, axis=-1)) 
        leaf_mask = np.all(image_resized != [0, 0, 0], axis=-1) 
        total_leaf_pixels = np.count_nonzero(leaf_mask)   
        severity_ratio = (diseased_pixels / total_leaf_pixels) * 100 if total_leaf_pixels > 0 else 0 
        
        print(f"Diseased Pixels: {diseased_pixels}") 
        print(f"Total Leaf Pixels: {total_leaf_pixels}")  
        print(f"Severity Ratio: {severity_ratio}%") 
        
        severity_ratio = ceil(severity_ratio * 1000) / 1000  
    return severity_ratio
