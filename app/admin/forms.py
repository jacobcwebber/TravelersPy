from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import DecimalField, FileField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from app import db
from app.models import User

class ChangeUserEmailForm(FlaskForm):
    email = EmailField('New email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(message="Email required."), Email(message="Not a valid email.")])
    first_name = StringField('First name', validators=[InputRequired(message="First name required."), Length(1, 64)])
    last_name = StringField('Last name', validators=[InputRequired(message="Last name required."), Length(1, 64)]) 
    password = PasswordField('Password', validators=[InputRequired(message="Password required."),
                                                     EqualTo('password2', 'Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[InputRequired(message="Confirm password required.")])
    submit = SubmitField('Create')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class DestinationForm(FlaskForm):
    name = StringField('Destination', validators=[InputRequired(message="Submit a destination name.")])
    country_id = SelectField('Country', choices=[], coerce=int)
    lat = DecimalField('Latitude', places=8, rounding=None, validators=[InputRequired()])
    lng = DecimalField('Longitude', places=8, rounding=None, validators=[InputRequired()])
    description = TextAreaField('Description')
    img_url = StringField('', validators=[InputRequired("Please upload a photo.")])
    img_upload = FileField('Upload a photo')
    tags = StringField('Tags', validators=[InputRequired(message="At least one tag required.")])
    submit = SubmitField('Create destination')

    def validate_country_id(self, field):
        if self.country_id.data == 0:
            raise ValidationError('Select a country.')
