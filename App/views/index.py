from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import create_user, initialize
from flask_jwt_extended import current_user, jwt_required

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
@jwt_required(optional=True)
def index_page():
    if current_user:
        return redirect("/upload-page")
    return redirect("login-page")

@index_views.route('/login-page', methods=['GET'])
def login_page():
    return render_template("index.html")

@index_views.route('/about-us-page', methods=['GET'])
def about_us_page():
    return  render_template('aboutUs.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})