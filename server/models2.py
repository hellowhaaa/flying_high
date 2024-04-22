from flask import Flask, render_template, abort, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, InputRequired
from bson.objectid import ObjectId
import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()], render_kw={"placeholder": "Username"}) 
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})
    email = EmailField('Email', validators=[InputRequired()],render_kw={"placeholder": "Email"})
    address = StringField('Address', validators=[InputRequired()], render_kw={"placeholder": "Address"})
    submit = SubmitField('Submit')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)
    

def create_user(username,password,email,address):
    body = {
        'username': username,
        'password': password,
        'email': email,
        'address': address,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
    return body