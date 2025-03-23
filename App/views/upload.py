from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import validate_upload, encode_image, get_all_uploads_json, get_upload, get_uploads_by_date, upload_image, upload_guest
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, current_user
import os
import base64

upload_views = Blueprint('upload_views', __name__, template_folder='../templates')

@upload_views.route('/upload-page', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@upload_views.route('/upload', methods=['POST'])
@jwt_required()
def upload_file(): 
    if 'file' not in request.files:
        flash("No file")
        return render_template("index.html")
    file = request.files['file']
    validated = validate_upload(file.filename)
    if validated:
        image = file.read()
        upload = upload_image(image, current_user.id)
        encoded_img = encode_image(image)
        return render_template("result.html", upload=upload, image=encoded_img)
    flash("Invalid file")
    return render_template("upload.html")

@upload_views.route('/upload-guest', methods=['POST'])
def upload_file_guest(): 
    if 'file' not in request.files:
        flash("No file")
        return render_template("index.html")
    file = request.files['file']
    validated = validate_upload(file.filename)
    if validated:
        image = file.read()
        upload = upload_guest(image)
        encoded_img = encode_image(image)
        return render_template("result.html", upload=upload, image=encoded_img)
    flash("Invalid file")
    return render_template("upload.html")

@upload_views.route("/api/image", methods=['POST'])
def get_image():
    file = request.files.get('file')  
    if not file:
        return jsonify({"error": "No file selected"})
    if validate_upload(file.filename):
        img = file.read()
        encoded_image = base64.b64encode(img).decode("UTF-8")
        return jsonify({"image" : encoded_image})
    return jsonify({"error": "Invalid image selected"})

@upload_views.route("/api/uploaded-image/<int:id>", methods=['GET'])
def get_uploaded_image(id):
    upload = get_upload(id)
    if not upload:
        return jsonify({"error": "Upload not found"})
    img = upload.image
    encoded_image = base64.b64encode(img).decode("UTF-8")
    return jsonify({"id" : upload.id, "date" : upload.date, "image" : encoded_image, "severity" : upload.severity, "type" : upload.disease_type, "actions" : upload.actions})


@upload_views.route("/api/uploads", methods=['GET'])
def display_uploads():
    uploads = get_all_uploads_json()
    return jsonify(uploads)

@upload_views.route("/history-page", methods=['GET'])
@jwt_required()
def history_page():
    uploads = get_uploads_by_date(current_user.id)
    dates = []
    count=0
    exists = False
    for upload in uploads:
        curr = upload.date
        for date in dates:
            if curr == date:
                exists = True
                break  
        if exists == False:
            dates.append(curr)
        else: 
            exists = False
    return render_template("history.html", uploads=uploads, dates=dates)