from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, verify_jwt_in_request
from App.models import User
from App.controllers.mail import validate_email_syntax, send_verification



def login(email, password):
  user = User.query.filter_by(email=email).first()
  if user and user.check_password(password):
    return create_access_token(identity=email)
  return None

def validate_email_address(email):
  if not validate_email_syntax(email):
    return None
  passcode = send_verification(email)
  if not passcode:
    return None
  return passcode
  


  
  
def setup_jwt(app):
  jwt = JWTManager(app)

  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    user = User.query.filter_by(email=identity).one_or_none()
    if user:
        return str(user.id)
    return None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)
  return jwt


def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          user_id = get_jwt_identity()
          current_user = User.query.get(user_id)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)