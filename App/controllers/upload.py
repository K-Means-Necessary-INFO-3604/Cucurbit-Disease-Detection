from App.disease_recommendations import DiseaseRecommendations
from App.models import Upload 
from App.database import db 
import cv2 
import base64 
from datetime import datetime 
import pytz 
import numpy as np 
from math import ceil 
import random
import numpy as np
import io
from PIL import Image
from rembg import remove, new_session
import geocoder
import xgboost as xgb
import torch
from torchvision import transforms, models


allowed = {'jpg', 'jpeg', 'png'} 

def upload_image(image, user_id): 
    ast = pytz.timezone("America/Port_of_Spain") 
    date = datetime.now(ast) 
    severity, disease = analyze_leaf(image)
    if severity is not None and disease is not None:
        action_list = get_disease_actions(disease)
        if action_list:
            actions=""
            for action in action_list:
                actions = actions + " " + action
            upload = Upload(image=image, date=date.date(), user_id=user_id, disease_type=disease, severity=severity, actions=actions) 
            db.session.add(upload) 
            db.session.commit() 
            return upload
    return None

def upload_guest(image): 
    ast = pytz.timezone("America/Port_of_Spain") 
    date = datetime.now(ast) 
    severity, disease = analyze_leaf(image) 
    if severity is not None and disease is not None:
        action_list = get_disease_actions(disease)
        if action_list:
            actions=""
            for action in action_list:
                actions = actions + " " + action
            upload = Upload(image=image, date=date.date(), disease_type=disease,severity=severity, actions=actions)  
            return upload
    return None

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


def segment_image(binary_data):
    binary_data = remove_background(binary_data)
    nparr = np.frombuffer(binary_data, np.uint8) 
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
    if image is None: 
        return None, None
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
    return diseased_only, image_resized
    

def analyze_leaf(binary_data):
    segmented_image, image_resized = segment_image(binary_data)
    severity = calculate_severity(segmented_image, image_resized)
    if severity is not None:
        image = Image.fromarray(segmented_image)
        features = extract_features(image)
        disease = classify_disease(model, features)
        if disease is None:
            return None, None
        return severity, disease
    return None, None
    

def calculate_severity(diseased_only, image_resized):
    
    if diseased_only is not None and image_resized is not None:
        diseased_pixels = np.count_nonzero(np.all(diseased_only != 0, axis=-1)) 
        leaf_mask = np.all(image_resized != [0, 0, 0], axis=-1) 

        total_leaf_pixels = np.count_nonzero(leaf_mask)   
        severity_ratio = (diseased_pixels / total_leaf_pixels) * 100 if total_leaf_pixels > 0 else 0 
        
        severity_ratio = ceil(severity_ratio * 1000) / 1000  
    else:
        return None
    return severity_ratio

def remove_background(binary_data):
    """Removes background from an image and returns it as binary data."""

    random.seed(0)
    np.random.seed(0)
    session = new_session("u2net", providers=["CUDAExecutionProvider"])

    image_io = io.BytesIO(binary_data)
    
    with Image.open(image_io).convert("RGBA") as img:
        img_array = np.array(img)
    
    image_without_background = remove(img_array, session=session)
    
    #Convert back to BytesIO and return as binary data
    image_io = io.BytesIO()
    Image.fromarray(image_without_background).save(image_io, format="PNG")
    image_io.seek(0)

    return image_io.read()

def get_lat_lng(address):
    ip = geocoder.ip(address)
    if ip.latlng:
        return ip.latlng
    else:
        return None


model = xgb.Booster()
model.load_model('ml_models/xgb_model_complete.json') 

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

resnet = models.resnet50(pretrained=True)


def extract_features(image):
    
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        x = resnet.conv1(image_tensor)
        x = resnet.bn1(x)
        x = resnet.relu(x)
        x = resnet.maxpool(x)
        x = resnet.layer1(x)
        x = resnet.layer2(x)
        x = resnet.layer3(x)
        x = resnet.layer4(x)
        x = resnet.avgpool(x)
        x = torch.flatten(x, 1)

    features = x.cpu().numpy().flatten() 
    return features

def classify_disease(model, image_features):
    dmatrix = xgb.DMatrix(image_features.reshape(1, -1))
    predictions = model.predict(dmatrix)
    print(predictions[0])
    name = get_disease_name(predictions[0])
    return name

def get_disease_name(disease):
    if disease == 1.0:
        return "Cucumber Anthracnose"
    if disease == 2.0:
        return "Cucumber Bacterial Wilt"
    if disease == 3.0:
        return "Cucumber Downy Mildew"
    if disease == 4.0:
        return "Cucumber Gummy Stem Blight"
    if disease == 5.0:
        return "Pumpkin Bacterial Leaf Spot"
    if disease == 6.0:
        return "Pumpkin Downy Mildew"
    if disease == 7.0:
        return "Pumpkin Mosaic"
    if disease == 8.0:
        return "Pumpkin Powdery Mildew"
    return None

def get_disease_videos(disease):
    disease = disease.title()
    
    if disease == "Cucumber Downy Mildew" or disease == "Pumpkin Downy Mildew":
        return DiseaseRecommendations.downy_mildew_videos()
        
    if disease == "Pumpkin Powdery Mildew":
        return DiseaseRecommendations.powdery_mildew_videos()
    
    if disease == "Pumpkin Mosaic Disease":
        return DiseaseRecommendations.mosaic_disease_videos()

    if disease == "Pumpkin Bacterial Leaf Spot":
        return DiseaseRecommendations.bacterial_leaf_spot_videos()

    if disease == "Cucumber Anthracnose":
        return DiseaseRecommendations.anthracnose_videos()
    
    if disease == "Cucumber Bacterial Wilt":
        return DiseaseRecommendations.bacterial_wilt_videos()
        
    if disease == "Cucumber Gummy Stem Blight":
        return DiseaseRecommendations.gummy_stem_blight_videos()
    
    return None

def get_disease_actions(disease):
    disease = disease.title()
    
    if disease == "Cucumber Downy Mildew" or disease == "Pumpkin Downy Mildew":
        return DiseaseRecommendations.downy_mildew()
        
    if disease == "Pumpkin Powdery Mildew":
        return DiseaseRecommendations.powdery_mildew()
    
    if disease == "Pumpkin Mosaic Disease":
        return DiseaseRecommendations.mosaic_disease()

    if disease == "Pumpkin Bacterial Leaf Spot":
        return DiseaseRecommendations.bacterial_leaf_spot()

    if disease == "Cucumber Anthracnose":
        return DiseaseRecommendations.anthracnose()
    
    if disease == "Cucumber Bacterial Wilt":
        return DiseaseRecommendations.bacterial_wilt()
        
    if disease == "Cucumber Gummy Stem Blight":
        return DiseaseRecommendations.gummy_stem_blight()
    
    return None