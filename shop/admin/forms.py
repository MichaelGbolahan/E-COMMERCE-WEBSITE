from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField,PasswordField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError
from flask_wtf.file import FileField,FileAllowed
from .models import Register

class RegisterUser(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    username=StringField('Username',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('confirm',message='password must match')])
    confirm=PasswordField('Repeat Password',validators=[DataRequired()])
    submit=SubmitField('Register')

    def validate_username(self,username):
        reg=Register.query.filter_by(username=username.data).first()
        if reg:
            raise ValidationError ('username is already taken. please choose a defferent one')


    def validate_username(self,email):
        reg=Register.query.filter_by(email=email.data).first()
        if reg:
            raise ValidationError ('username is already taken. please choose a defferent one')


class LoginAdmin(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')


