from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(Form):
    email = StringField('', [
        validators.Email(message = "Please submit a valid email"),
        validators.Length(min=4, max=50, message='Email must be 5 to 50 character long')
        ], render_kw={"placeholder": "Email"})
    firstName = StringField('', [
        validators.InputRequired()
    ], render_kw={"placeholder": "First name"})
    lastName = StringField('', [
        validators.InputRequired()
    ], render_kw={"placeholder": "Last name"}) 
    password = PasswordField('', [
        validators.DataRequired(),
    ], render_kw={"placeholder": "Password"})

class CountryForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=300)])
    description = TextAreaField('Description')

class DestinationForm(Form):
    # cur = connection.cursor()

    # cur.execute("SELECT CountryID, CountryName "
    #             "FROM countries")

    # countries = cur.fetchall()
    # cur.close()

    countriesList = [(0, "")]
    # for country in countries:
    #     countriesList.append((country['CountryID'], country['CountryName']))

    name = StringField('Name')
    countryId = SelectField('Country', choices=countriesList, coerce=int)
    category = SelectField('Category', choices=[
        (0, ""),
        (1, "Natural Site"),
        (2, "Cultural Site"),
        (3, "Activity")], coerce=int)
    lat = DecimalField('Latitude', places=8, rounding=None)
    lng = DecimalField('Longitude', places=8, rounding=None)
    description = TextAreaField('Description')
    imgUrl = StringField('Image Upload', [validators.URL(message="Not a valid url")])
    tags = StringField('Tags')