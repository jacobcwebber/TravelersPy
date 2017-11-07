from flask import Flask, request, render_template, url_for, logging, session, flash, redirect
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from functools import wraps
import re

app = Flask(__name__)

connection = pymysql.connect(host='localhost',
                             user='Jacob',
                             password='691748jw',
                             db='traveler',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

class RegisterForm(Form):
    username = StringField('', [
        validators.Length(min=4, max=25, message='Username must be 4 to 25 characters long')
        ], render_kw={"placeholder": "username"})
    email = StringField('', render_kw={"placeholder": "email"})
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ], render_kw={"placeholder": "password"})
    confirm = PasswordField('', render_kw={"placeholder": "confirm password"})

    def validate_email(form, field):
        if len(field.data) < 5 or len(field.data) > 35:
            raise ValidationError('Email must be 5 to 35 characters long')
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", field.data):
            raise ValidationError('Please submit a valid email')

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = connection.cursor()
        cur.execute("INSERT INTO user(Username, Password, Email) VALUES (%s, %s, %s)", (username, password, email))

        connection.commit()
        cur.close()

        flash('Congratulations! You are now registered.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

#authenticates login details; logs user in and changes session details if passes
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_attempt = request.form['password']

        cur = connection.cursor()

        result = cur.execute("SELECT * FROM user WHERE Username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['Password']

            #checks if passwords match and logs you in if they do
            if sha256_crypt.verify(password_attempt, password):
                session['logged_in'] = True
                session['username'] = username

                #sets admin session status from db query
                cur.execute("SELECT IsAdmin FROM User WHERE Username = %s", [username])
                if cur.fetchone()['IsAdmin'] == 1:
                    session['admin'] = True
                else:
                    session['admin'] = False

                flash('Welcome, ' + username + '. You are now logged in.', 'success')
                return redirect(url_for('index'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()

        else:
            error = "Username not found"
            return render_template('login.html', error=error)

    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized, please login.', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['admin'] == True:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized. Requires administrator access.', 'danger')
            return redirect(url_for('index'))
    return

@app.route('/countries')
@is_logged_in
def countries():
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM countries")
    countries = cur.fetchall()

    if result > 0:
        return render_template('countries.html', countries=countries)
    else:
        msg = 'No countries found.'
        return render_template('countries.html', msg=msg)

    cur.close()

@app.route('/country/<string:id>')
@is_logged_in
def country(id):
    cur = connection.cursor()
    try:
        result = cur.execute("SELECT * FROM countries WHERE CountryID = %s", [id])
        country = cur.fetchone()
        return render_template('country.html', country=country)
    except:
        msg = "Country does not exist."
        return render_template('country.html', msg=msg)


class DestinationForm(Form):
    cur = connection.cursor()

    cur.execute("SELECT CountryID, countryName FROM countries")
    countries = cur.fetchall()

    #countriesList = countries.items()
    #print(countriesList)

    name = StringField('Name', [validators.Length(min=1, max=300)])
    #countryId = SelectField('Country', choices=countriesList)
    category = SelectField('Category', choices=[(1, "Natural Site"), (2, "Cultural Site"), (3, "Historic Site")])
    description = TextAreaField('Description')

@app.route('/create-destination')
@is_logged_in
@is_admin
def create_destination():
    form = DestinationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        country = form.country.data
        description = form.description.data

        cur = connection.cursor()

        cur.execute("INSERT INTO destinations(DestName, CountryID, Description) VALUES (%s, %s, %s)")

    return render_template('create_destination.html', form=form)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key='supersecretkey'
    app.run(port=8000, debug=True)
