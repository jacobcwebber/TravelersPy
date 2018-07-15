from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from app import db
from app.models import User

class NewUserForm(InviteUserForm):
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