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
        cur.execute("INSERT INTO users(Username, Password, Email) VALUES (%s, %s, %s)", (username, password, email))

        connection.commit()
        cur.close()

        flash('Congratulations! You are now registered.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_attempt = request.form['password']

        cur = connection.cursor()

        result = cur.execute("SELECT * FROM users WHERE Username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['Password']

            #checks if passwords match and logs you in if they do
            if sha256_crypt.verify(password_attempt, password):
                session['logged_in'] = True
                session['username'] = username

                #sets admin session status from db query
                cur.execute("SELECT IsAdmin FROM users WHERE Username = %s", [username])
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

    cur.execute("SELECT CountryID, CountryName FROM countries")
    countries = cur.fetchall()

    countriesList = [(0, "")]
    for country in countries:
        countriesList.append((country['CountryID'], country['CountryName']))

    name = StringField('Name', [validators.Length(min=1, max=300)])
    countryId = SelectField('Country', choices=countriesList, coerce=int)
    category = SelectField('Category', choices=[(0, ""), (1, "Natural Site"), (2, "Cultural Site"), (3, "Historic Site")], coerce=int)
    description = TextAreaField('Description')

@app.route('/create-destination', methods=['POST', 'GET'])
@is_logged_in
def create_destination():
    form = DestinationForm(request.form)
    if request.method == 'POST' and form.validate():
        print(form.category)

        name = form.name.data
        countryId = form.countryId.data
        category = form.category.data
        description = form.description.data

        cur = connection.cursor()

        cur.execute("INSERT INTO destinations(DestName, CountryID, Category, Description) VALUES (%s, %s, %s, %s)", (name, countryId, category, description))

        connection.commit()
        cur.close()

        flash('Your new destination has been created!', 'success')

        return redirect(url_for('destinations'))

    return render_template('create_destination.html', form=form)

@app.route('/destinations')
@is_logged_in
def destinations():
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM destinations d JOIN countries c ON d.CountryID = c.CountryID")
    destinations = cur.fetchall()

    if result > 0:
        return render_template('destinations.html', destinations=destinations)
    else:
        msg="No destinations found."
        return render_template('destinations.html',  msg=msg)

    cur.close()


@app.route('/destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def destination(id):
    if request.method == 'GET':
        cur = connection.cursor()
        result = cur.execute("SELECT * FROM destinations WHERE DestID = %s", [id])
        destination = cur.fetchone()

        if result > 0:
            return render_template('destination.html', destination=destination)
        else:
            flash('Destination does not exist.', 'danger')
            return redirect(url_for('destinations'))

    else:
        cur = connection.cursor()
        cur.execute("INSERT INTO favorites VALUES (%s, %s)", (session['username'], int(id)) )

        connection.commit()
        cur.close()
        return render_template('destination.html', destination=int(id))

@app.route('/edit_destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_destination(id):
    cur = connection.cursor()
    cur.execute("SELECT * FROM destinations WHERE DestID = %s", [id])
    destination = cur.fetchone()
    cur.close()

    form = DestinationForm(request.form)
    #fill in form with info from db
    form.name.data = destination['DestName']
    form.countryId.data = destination['CountryID']
    form.category.data = destination['Category']
    form.description.data = destination['Description']

    if request.method == 'POST':
        name = form.name.data
        countryId = form.countryId.data
        category = form.category.data
        description = form.description.data

        cur = connection.cursor()
        cur.execute("UPDATE destinations SET DestName=%s, CountryID=%s, Category=%s, Description=%s WHERE DestID = %s", (name, countryId, category, description, id))
        connection.commit()
        cur.close()

        flash('Destination updated.', 'success')

        return redirect(url_for('destinations'))

    return render_template('edit_destination.html', form=form)

@app.route('/account')
@is_logged_in
def account():
    cur = connection.cursor()
    cur.execute("SELECT f.DestID, DestName FROM favorites f JOIN destinations d ON d.DestID = f.DestID WHERE Username = %s", [session['username']])
    favorites = cur.fetchall()

    return render_template('account.html', favorites=favorites)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key='supersecretkey'
    app.run(port=8000, debug=True)
