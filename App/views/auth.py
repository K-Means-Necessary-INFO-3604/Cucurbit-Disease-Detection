from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
import random

from.index import index_views

from App.controllers import (
    login,
    create_user,
    user_exists,
    confirm_password,
    get_all_users,
    validate_email_address,
    create_new_token,
)

from App.encryption import encrypt, decrypt

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    
@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.email}")


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['email'], data['password'])
    response = redirect("/upload-page")
    if not token:
        flash('Bad email or password given'), 401
        response = redirect("/")
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/signup', methods=['GET','POST'])
def signup_action():

    if request.method == 'GET':
        return render_template("index.html", signup=True)
    
    data = request.form
    email = data['email']
    password = data['password']
    confirmation = data['password2']

    if user_exists(email) == True:
        flash("User already exists")
        return render_template("index.html", signup=True)
    if confirm_password(password, confirmation) == False:
        flash("Passwords do not match")
        return render_template("index.html", signup=True)
    
    passcode = validate_email_address(email)
    if not passcode:
        flash("Please enter a valid email")
        return render_template("index.html", signup=True)
    passcode = encrypt(str(passcode))
    password = encrypt(str(password))
    return redirect(url_for('auth_views.verification_page', email=email, passcode=passcode, password=password))

@auth_views.route("/verification", methods=['GET'])
def verification_page():
    email = request.args.get('email')
    passcode = request.args.get('passcode')
    password = request.args.get('password')
    if email and passcode:
        return render_template("awaiting_verification.html", email=email, passcode=passcode, password=password)
    else:
        flash("Error during verification")
        return render_template("index.html", signup=True)

@auth_views.route("/verify", methods=['POST'])
def verify_email():
    user_passcode = request.form.get('passcode')
    encoded_passcode = request.form.get('encoded')
    email = request.form.get('email')
    encoded_password = request.form.get('password')
    passcode = decrypt(encoded_passcode)
    password = decrypt(encoded_password)
    
    if user_passcode == passcode:
        if user_exists(email) == True:
            flash("User already exists")
            return redirect("/")
        create_user(email, password)
        token = login(email,password)
        flash("User created")
        response = redirect("/upload-page")
        set_access_cookies(response, token)
        return response
    else:
        flash("Invalid verification code")
        return render_template("awaiting_verification.html", email=email, passcode=encoded_passcode, password=encoded_password)


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect("/") 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['email'], data['password'])
  if not token:
    return jsonify(message='bad email or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"email: {current_user.email}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/token', methods=['GET'])
@jwt_required()
def token():
    if current_user.email == "admin":
        return render_template("refresh.html")
    return redirect("/")

@auth_views.route('/new-token', methods=['POST'])
@jwt_required()
def new_token():
    if current_user.email == "admin":
        token = request.form['token']
        status = create_new_token(token)
        if status:
            flash("Successful")
        else:
            flash("Error")
    return redirect("/")