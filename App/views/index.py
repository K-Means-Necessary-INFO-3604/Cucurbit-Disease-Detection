from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import create_user, initialize
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/developing', methods=['GET'])
def developing():
    return  render_template('in_progress.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

