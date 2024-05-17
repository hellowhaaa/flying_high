from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import InputRequired


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})
    email = EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "Email"})
    address = StringField('Address', validators=[InputRequired()], render_kw={"placeholder": "Address"})
    submit = SubmitField('Register')
    
    

