from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField,PasswordField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError
from flask_wtf.file import FileField,FileAllowed
from .models import RegisterCustomer

class CustomerRegistrationForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('Email:', validators=[Email(), DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match!')])
    confirm = PasswordField('Repeat password:', validators=[DataRequired()])
    country = StringField('Country:', validators=[DataRequired()])
    city = StringField('City:', validators=[DataRequired()])
    contact = StringField('Contact:', validators=[DataRequired()])
    address = StringField('Address:', validators=[DataRequired()])
    zipcode = StringField('Zip code:', validators=[DataRequired()])
    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only please!')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = RegisterCustomer.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already in use!")

    def validate_email(self, email):
        user = RegisterCustomer.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email address is already in use!")

class LoginCustomer(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')