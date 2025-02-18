from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import create_user
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required

upload_views = Blueprint('upload_views', __name__, template_folder='../templates')

@upload_views.route('/uploadPage', methods=['GET'])
def upload_page():
    return render_template('upload.html')