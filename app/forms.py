from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    email = StringField('', validators=[InputRequired()], render_kw={"placeholder": "Email"})
    first_name = StringField('', validators=[InputRequired()], render_kw={"placeholder": "First name"})
    last_name = StringField('', validators=[InputRequired()], render_kw={"placeholder": "Last name"}) 
    password = PasswordField('', validators=[InputRequired()], render_kw={"placeholder": "Password"})

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