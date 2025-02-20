from App.models import User
from App.database import db

def create_user(email, password):
    newuser = User(email=email, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def user_exists(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return True
    return False

def confirm_password(password, confirmation):
    if password == confirmation:
        return True
    return False

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def get_user(id):
    return User.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, email):
    user = get_user(id)
    if user:
        user.email = email
        db.session.add(user)
        return db.session.commit()
    return None
    