from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message="Email required."), Email(message="Not a valid email.")])
    password = PasswordField('Password', validators=[InputRequired(message="Password required.")])
    remember_me = BooleanField('Remember Me')
    login = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message="Email required."), Email(message="Not a valid email.")])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()]) 
    password = PasswordField('Password', validators=[InputRequired(message="Password required.")])
    register = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    about = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[InputRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class CountryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = TextAreaField('Description')

class DestinationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    country_id = SelectField('Country', choices=[], coerce=int, validators=[InputRequired()])
    lat = DecimalField('Latitude', places=8, rounding=None, validators=[InputRequired()])
    lng = DecimalField('Longitude', places=8, rounding=None, validators=[InputRequired()])
    description = TextAreaField('Description')
    img_url = StringField('Image Upload', validators=[InputRequired()])
    tags = StringField('Tags', validators=[InputRequired(message="At least one tag required.")])
