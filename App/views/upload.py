from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import validate_upload, encode_image
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
import os
import base64

upload_views = Blueprint('upload_views', __name__, template_folder='../templates')

@upload_views.route('/uploadPage', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@upload_views.route('/upload', methods=['POST'])
def upload_image(): 
    if 'file' not in request.files:
        flash("No file")
        return render_template("index.html")
    file = request.files['file']
    validated = validate_upload(file.filename)
    if validated:
        filename = secure_filename(file.filename)
        file.save(os.path.join("App/uploads", filename))
        flash("file found")
        filepath = "App/uploads/" + filename
        upload = encode_image(filepath)
        return render_template("in_progress.html", upload=upload)
    flash("Invalid file")
    return render_template("upload.html")

@upload_views.route("/api/image", methods=['POST'])
def get_image():
    file = request.files.get('file')  
    if not file:
        return jsonify({"error": "No file selected"})
    if validate_upload(file.filename):
        img = file.read()
        encode_image = base64.b64encode(img).decode("UTF-8")
        return jsonify({"image" : encode_image})
    return jsonify({"error": "Invalid image selected"})