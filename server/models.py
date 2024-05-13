from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, InputRequired
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})
    email = EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "Email"})
    address = StringField('Address', validators=[InputRequired()], render_kw={"placeholder": "Address"})
    submit = SubmitField('Register')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    
def create_user(username, password, email, address):
    hashed_password = generate_password_hash(password)
    return {
        'username': username,
        'password': hashed_password,
        'email': email,
        'address': address,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }


def same_username(collection, username):
    return collection.find_one({'username': username}) is not None


def check_user_credentials(collection, username, password):
    user = collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return user
    return None
