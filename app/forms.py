from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired(), Email()])
    last_name = StringField('Last Name', validators=[InputRequired()]) 
    password = PasswordField('Password', validators=[InputRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CountryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = TextAreaField('Description')

class DestinationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    countryId = SelectField('Country', choices=['USA', 'Canada'], coerce=int, validators=[InputRequired()])
    lat = DecimalField('Latitude', places=8, rounding=None, validators=[InputRequired()])
    lng = DecimalField('Longitude', places=8, rounding=None, validators=[InputRequired()])
    description = TextAreaField('Description')
    imgUrl = StringField('Image Upload', validators=[InputRequired()])
    tags = StringField('Tags', validators=[InputRequired(message="At least one tag required.")])
    submit  = SubmitField('Create Destination')