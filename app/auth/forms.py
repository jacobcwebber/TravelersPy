from flask import url_for, Markup
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import BooleanField, DecimalField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from app.models import User

class LoginForm(FlaskForm):
    email = EmailField('Email', id="login-email", validators=[InputRequired(message="Email required."), Length(1, 120), Email(message="Not a valid email.")])
    password = PasswordField('Password', id="login-password", validators=[InputRequired(message="Password required.")])
    remember_me = BooleanField('Keep me logged in')
    login = SubmitField('Log In')   

class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(message="Email required."), Email(message="Not a valid email.")])
    first_name = StringField('First name', validators=[InputRequired(message="First name required."), Length(1, 64)])
    last_name = StringField('Last name', validators=[InputRequired(message="Last name required."), Length(1, 64)]) 
    password = PasswordField('Password', validators=[InputRequired(message="Password required."),
                                                     EqualTo('password2', 'Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[InputRequired(message="Confirm password required.")])
    register = SubmitField('Register')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError(Markup('Email already registered. Did you mean to '
                                  '<a href="{}" class="text-red text-underline">log in</a> instead?'.format(
                url_for('auth.login'))))

class EditProfileForm(FlaskForm):
    about = TextAreaField('About me', validators=[Length(0, 140)])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Length(1, 120), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New password', validators=[InputRequired()])
    new_password2 = PasswordField('Confirm new Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ChangeEmailForm(FlaskForm):
    email = EmailField('New email', validators=[InputRequired(), Length(1, 120), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update email')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')