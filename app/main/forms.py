from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField
from wtforms.validators import InputRequired

class DestinationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    country_id = SelectField('Country', choices=[], coerce=int, validators=[InputRequired()])
    lat = DecimalField('Latitude', places=8, rounding=None, validators=[InputRequired()])
    lng = DecimalField('Longitude', places=8, rounding=None, validators=[InputRequired()])
    description = TextAreaField('Description')
    img_url = StringField('Image Upload', validators=[InputRequired()])
    tags = StringField('Tags', validators=[InputRequired(message="At least one tag required.")])

class SearchForm(FlaskForm):
    location = StringField('Location')
    keywords = StringField('Keywords')
