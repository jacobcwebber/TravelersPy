from flask import Flask, request, render_template, url_for, logging, session, flash, redirect, Markup, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql.cursors
from passlib.hash import sha256_crypt # TODO: change this to flask encryption
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, FileField, ValidationError, DecimalField #TODO: get rid of this
from functools import wraps
import re #TODO: move to the one place I'm using this
import sys
import json
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

connection = pymysql.connect(host='localhost',
                             user='Jacob',
                             password=os.environ['DATABASE_PASSWORD'],
                             db='travelers',
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
        if session['is_admin'] == True:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized. Requires administrator access.', 'danger')
            return redirect(url_for('index'))
    return

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


#####################################################
#####          USER FUNCTIONALITY                ####
#####################################################

#Forms
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

@app.route('/', methods=['POST', 'GET'])
def index():
    form = RegisterForm(request.form)

    if request.method == 'POST':
        if request.form['submit'] == "Create account":
            email = form.email.data
            first = form.firstName.data
            last = form.lastName.data
            password = sha256_crypt.encrypt(str(form.password.data))

            cur = connection.cursor()
            cur.execute("INSERT INTO users(FirstName, LastName, Password, Email) "
                        "VALUES (%s, %s, %s, %s, %s)"
                        , (first, last, password, email))

            connection.commit()
            cur.close()

            flash('Congratulations! You are now registered.', 'success')

            return redirect(url_for('login'))
        elif request.form['submit'] == "Login":
            email = request.form['email']
            password_attempt = request.form['password']

            cur = connection.cursor()
            result = cur.execute("SELECT * "
                                "FROM users "
                                "WHERE Email = %s"
                                , [email])
            user = cur.fetchone()
            cur.close()

            if result > 0:
                password = user['Password']
                userId = user['UserID'] 
                firstname = user['FirstName']
                isAdmin = user['IsAdmin']

                if sha256_crypt.verify(password_attempt, password):
                    
                    session['user'] = userId
                    session['logged_in'] = True
                    session['is_admin'] = isAdmin

                    return redirect(url_for('destinations'))

                else:
                    error = 'Invalid login. Please try again.'
                    return render_template('login.html', error=error)
                cur.close()

            else:
                error = "User not found."
                return render_template('login.html', error=error)

    return render_template('home.html', form=form)

def login():
    password_attempt = request.form['password']

    cur = connection.cursor()

    result = cur.execute("SELECT * "
                            "FROM users "
                            "WHERE Username = %s"
                            , [username])
    user = cur.fetchone()
    cur.close()

    if result > 0:
        password = user['Password']
        userId = user['UserID'] 
        firstname = user['FirstName']

        if sha256_crypt.verify(password_attempt, password):
            
            # set session variables
            session['logged_in'] = True
            session['user'] = userId

            if user['IsAdmin'] == 1:
                session['is_admin'] = True
            else:
                session['is_admin'] = False

            return redirect(url_for('index'))

        else:
            error = 'Invalid login'
            return render_template('login.html', error=error)
        cur.close()

    else:
        error = "Username not found."
        return render_template('login.html', error=error)

@app.route('/change-map', methods=['POST'])
def change_map():
    view = request.form['view']

    cur = connection.cursor()

    if view == "all":
        cur.execute("SELECT l.Lat, l.Lng, d.DestName "
                    "FROM dest_locations l JOIN destinations d on l.DestID = d.DestID")
    elif view == "favorites":
        cur.execute("SELECT l.Lat, l.Lng, d.DestName "
                    "FROM dest_locations l JOIN destinations d on l.DestID = d.DestID "
                    "WHERE l.DestID IN "
                        "(SELECT f.DestID "
                        "FROM favorites f "
                        "WHERE UserID = %s)"
                        , [session['user']])
    else:
        cur.execute("SELECT l.Lat, l.Lng, d.DestName "
                    "FROM dest_locations l JOIN destinations d on l.DestID = d.DestID "
                    "WHERE l.DestID IN "
                        "(SELECT e.DestID "
                        "FROM explored e "
                        "WHERE UserID = %s)"
                        , [session['user']])

    locations = cur.fetchall()
    cur.close()

    locationsList = []
    for location in locations:
        locationsList.append([float(location['Lat']), float(location['Lng']), location['DestName']])

    return jsonify(locationsList)

@app.route('/favorites')
@is_logged_in
def favorites():
    cur = connection.cursor()
    cur.execute('SELECT d.DestID, DestName, ImgUrl '
                'FROM favorites f JOIN destinations d ON f.DestID = d.DestID '
                                 'JOIN dest_images i ON d.DestID = i.DestID '
                'WHERE f.UserID = %s'
                , session['user'])
    favorites = cur.fetchall()
    
    return render_template('favorites.html', favorites=favorites)

@app.route('/explored')
@is_logged_in
def explored(): 
    cur = connection.cursor()
    cur.execute('SELECT d.DestID, DestName, ImgUrl '
                'FROM explored e JOIN destinations d ON e.DestID = d.DestID '
                                'JOIN dest_images i ON d.DestID = i.DestID '
                'WHERE e.UserID = %s'
                , session['user'])
    explored = cur.fetchall()

    return render_template('explored.html', explored=explored)

@app.route('/profile')
@is_logged_in
def profile():
    cur = connection.cursor()
    cur.execute("SELECT FirstName "
                "FROM users "
                "WHERE UserID = %s"
                , session['user'])
    user = cur.fetchone()

    cur.execute("SELECT f.DestID "
                "FROM favorites f JOIN destinations d ON d.DestID = f.DestID JOIN users u on u.UserID = f.UserID "
                "WHERE f.UserID = %s"
                , session['user'])
    favorites = cur.fetchall()
    
    cur.execute("SELECT DestID "
                "FROM explored "
                "WHERE UserID = %s"
                , session['user'])
    explored = cur.fetchall()

    cur.execute("SELECT c.CountryID "
                "FROM explored e JOIN destinations d ON e.DestID = d.DestID JOIN countries c ON d.CountryID = c.CountryID "
                "WHERE e.UserID = %s "
                "GROUP BY c.CountryID"
                , session['user'])
    countries = cur.fetchall()

    cur.execute("SELECT d.DestID "
                "FROM explored e JOIN destinations d ON e.DestID = d.DestID "
                                "JOIN dest_tags dt ON  dt.DestID = d.DestID "
                                "JOIN tags t ON t.TagID = dt.TagID "
                "WHERE e.UserID = %s AND t.TagName = 'UNESCO'"
                , session['user'])
    unesco = cur.fetchall()

    cur.execute("SELECT l.Lat, l.Lng, d.DestName "
                "FROM dest_locations l JOIN destinations d on l.DestID = d.DestID")
    locations = cur.fetchall()
    cur.close()
    
    locationsList = []
    for location in locations:
        locationsList.append([float(location['Lat']), float(location['Lng']), location['DestName']])

    counts = [len(explored), len(favorites), len(countries), len(unesco)]
    captions = ['Explored', 'Favorites', 'Countries Visited', 'UNESCO Sites Visited']

    return render_template('profile.html', user=user, favorites=favorites, explored=explored, locations=locationsList, captions=captions, counts=counts)

@app.route('/search')
def search():
    location = request.args.get('location')
    keyword = request.args.get('keywords')

    cur = connection.cursor()
    if location:
        if keyword:
            cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl, ContName '
                        'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
                                            'JOIN countries c ON c.CountryID = d.CountryID '
                                            'JOIN regions r ON c.RegionID = r.RegionID '
                                            'JOIN continents co ON co.ContID = r.ContID '
                                            'JOIN dest_tags dt ON dt.DestID = d.DestID '
                                            'JOIN tags t ON dt.TagID = t.TagID '
                        'WHERE (c.CountryName = %s OR ContName = %s OR r.RegionName = %s) AND t.TagName = %s '
            , (location, location, location, keyword)) 
        else:
            cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl, ContName '
                        'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
                                            'JOIN countries c ON c.CountryID = d.CountryID '
                                            'JOIN regions r ON c.RegionID = r.RegionID '
                                            'JOIN continents co ON co.ContID = r.ContID '
                        'WHERE (c.CountryName = %s or ContName = %s OR r.RegionName = %s)'
            , (location, location, location))
    elif keyword:
        cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl, ContName '
                    'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
                                        'JOIN countries c ON c.CountryID = d.CountryID '
                                        'JOIN regions r ON c.RegionID = r.RegionID '
                                        'JOIN continents co ON co.ContID = r.ContID '
                                        'JOIN dest_tags dt ON dt.DestID = d.DestID '
                                        'JOIN tags t on dt.TagID = t.TagID '
                    'WHERE t.TagName = %s'
        , keyword)   
    else:
        cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl    '
                    'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
                                        'JOIN countries c ON c.CountryID = d.CountryID '
                    'ORDER BY RAND() '
                    'LIMIT 5 '
                )
    destinations = cur.fetchall()

    # Add list of tags to the dictionaries for each destination
    for dest in destinations:
        cur.execute('SELECT TagName '
                    'FROM vTags '
                    'WHERE DestName = %s'
                    , dest['DestName'])
        tags = cur.fetchall()

        tagsList = [tag['TagName'] for tag in tags]
        dest['Tags'] = tagsList

    cur.execute("SELECT DestID "
                "FROM favorites "
                "WHERE UserID = %s"
                , session['user'])
    favs = cur.fetchall()

    cur.execute("SELECT DestID "
                "FROM explored "
                "WHERE UserID = %s"
                , session['user'])
    exp = cur.fetchall()

    favorites = [dest['DestID'] for dest in favs]
    explored = [dest['DestID'] for dest in exp]

    cur.execute('SELECT TagName FROM tags')
    tags = cur.fetchall()

    cur.execute('SELECT CountryName FROM countries')
    countries = cur.fetchall()

    cur.execute('SELECT ContName FROM continents')
    continents = cur.fetchall()

    cur.execute('SELECT RegionName FROM regions')
    regions = cur.fetchall()
    cur.close()

    countriesList = [country['CountryName'] for country in countries]
    continentsList = [continent['ContName'] for continent in continents]
    regionsList = [region['RegionName'] for region in regions]
    tagsList = [tag['TagName'] for tag in tags]

    locationsList = list(set(countriesList).union(set(list(set(continentsList).union(set(regionsList))))))
    
    return render_template('search.html', location=location, keyword=keyword, destinations=destinations, explored=explored, favorites=favorites, locationsList=locationsList, tagsList=tagsList)

@app.route('/alter-featured-dest', methods=['POST'])
def alter_featured_dest():
    data = request.values

    cur = connection.cursor()
    cur.execute("SELECT DestName, CountryName, d.DestID, c.CountryID, d.Description, ImgUrl "
                "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                                    "JOIN dest_images i ON d.DestID = i.DestID "
                                    "JOIN dest_locations l ON d.DestID = l.DestID "
                "WHERE d.DestID = %s"
                , data['id'])
    destination = cur.fetchone()

    cur.execute("SELECT TagName "
                "FROM vTags "
                "WHERE DestName  = %s"
                , destination['DestName'])
    tags = cur.fetchall()
    cur.close()

    return jsonify(destination, tags)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('index'))

#####################################################
#####             COUNTRIES PAGES                ####
#####################################################

class CountryForm(Form):
    cur = connection.cursor()

    name = StringField('Name', [validators.Length(min=1, max=300)])
    description = TextAreaField('Description')

@app.route('/countries')
@is_logged_in
def countries():
    cur = connection.cursor()
    result = cur.execute("SELECT c.CountryName, count(d.DestName) AS DestCount, c.CountryID "
                         "FROM countries c LEFT OUTER JOIN destinations d ON c.CountryID = d.CountryID "
                         "GROUP BY c.CountryName "
                         "ORDER BY c.CountryName")

    countries = cur.fetchall()
    cur.close()

    return render_template('countries.html', countries=countries)

@app.route('/country/<string:id>')
@is_logged_in
def country(id):
    cur = connection.cursor()

    cur.execute("SELECT CountryName, UpdateDate "
                        "FROM countries "
                        "WHERE CountryID = %s"
                        , [id])
    country = cur.fetchone()
    
    cur.execute("SELECT CountryName, DestName, DestID , c.UpdateDate"
                " FROM countries c JOIN destinations d"
                " WHERE c.CountryID = d.CountryID AND c.CountryID = %s"
                , [id])
    destinations = cur.fetchall()

    cur.execute("SELECT c.CountryId, d.DestName, i.ImgUrl "
            "FROM countries c JOIN destinations d ON c.CountryID = d.CountryID "
            "JOIN dest_images i on d.DestID = i.DestID "
            "WHERE c.CountryID = %s "
            "ORDER BY RAND()"
            , [id])
    images = cur.fetchall()
    cur.close()

    return render_template('country.html', country=country, destinations=destinations, images=images)


@app.route('/edit-country/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_country(id):
    cur = connection.cursor()
    cur.execute("SELECT CountryName, Description "
                "FROM countries "
                "WHERE CountryID = %s"
                , [id])

    country = cur.fetchone()
    cur.close()

    form = CountryForm(request.form)

    form.name.data = country['CountryName']
    form.description.data = country['Description']

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        cur = connection.cursor()
        cur.execute("UPDATE countries "
                    "SET CountryName=%s, Description=%s "
                    "WHERE CountryID=%s"
                    ,(name, description, id))

        connection.commit()
        cur.close()

        return redirect(url_for('countries'))

    return render_template('edit_country.html', form=form)

#####################################################
#####            DESTINATIONS PAGES              ####
#####################################################

@app.route('/destinations')
@is_logged_in
def destinations():
    cur = connection.cursor()
    cur.execute("SELECT d.DestID, DestName, ImgUrl "
                "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
                "ORDER BY d.UpdateDate DESC")
    recent = cur.fetchall()

    cur.execute("SELECT d.DestID, d.DestName, i.ImgUrl, count(f.DestID) AS Favorites "
                "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
                                    "JOIN favorites f on d.destID = f.DestID "
                "GROUP BY f.DestID "
                "ORDER BY Favorites DESC")
    popular = cur.fetchall()

    cur.execute("SELECT DestID "
                "FROM favorites "
                "WHERE UserID = %s"
                , session['user'])
    favs = cur.fetchall()

    cur.execute("SELECT DestID "
                "FROM explored "
                "WHERE UserID = %s"
                , session['user'])
    exp = cur.fetchall()
    cur.close()

    favorites = []
    for dest in favs:
        favorites.append(dest['DestID'])

    explored = []
    for dest in exp:
        explored.append(dest['DestID'])

    cur = connection.cursor()
    cur.execute("SELECT COUNT(*) AS Count "
                "FROM Destinations")
    count = cur.fetchone()

    return render_template('destinations.html', count=count, favorites=favorites, explored=explored, recent=recent, popular=popular)

@app.route('/destinations-admin')
@is_logged_in
def destinations_admin():
    cur = connection.cursor()
    cur.execute("SELECT * "
                "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                "ORDER BY d.DestName")

    destinations = cur.fetchall()
    cur.close() 

    return render_template('destinations_admin.html', destinations=destinations)

@app.route('/destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def destination(id):
    try:
        cur = connection.cursor()
        cur.execute("SELECT DestName, CountryName, d.DestID, c.CountryID, d.Description, ImgUrl, Lat, Lng "
                    "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                                        "JOIN dest_images i ON d.DestID = i.DestID "
                                        "JOIN dest_locations l ON d.DestID = l.DestID "
                    "WHERE d.DestID = %s"
                    , [id])
        destination = cur.fetchone()

        cur.execute("SELECT * "
                    "FROM vTags "
                    "WHERE DestName  = %s"
                    , destination['DestName'])
        tags = cur.fetchall()
        cur.close()

        return render_template('destination.html', destination=destination, tags=tags)

    except:
        flash('Destination does not exist.', 'danger')
        return redirect(url_for('destinations')) 

class DestinationForm(Form):
    cur = connection.cursor()

    cur.execute("SELECT CountryID, CountryName "
                "FROM countries")

    countries = cur.fetchall()
    cur.close()

    countriesList = [(0, "")]
    for country in countries:
        countriesList.append((country['CountryID'], country['CountryName']))

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

@app.route('/create-destination', methods=['POST', 'GET'])
@is_logged_in
def create_destination():
    form = DestinationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        countryId = form.countryId.data
        category = form.category.data
        description = form.description.data
        imgUrl = form.imgUrl.data
        tags = form.tags.data
        lat = form.lat.data
        lng = form.lng.data

        cur = connection.cursor()

        cur.execute("INSERT INTO destinations(DestName, CountryID, Category, Description) "
                    " VALUES (%s, %s, %s, %s)"
                    , (name, countryId, category, description))

        connection.commit()
        cur.close()

        cur = connection.cursor()

        cur.execute("SELECT DestID "
                    "FROM destinations "
                    "WHERE DestName = %s"
                    , [name])
        id = cur.fetchone()

        cur.execute("INSERT INTO dest_images "
                    " VALUES (%s, %s)",
                    (id['DestID'], imgUrl))
        connection.commit()

        cur.execute("INSERT INTO dest_locations "
                    " VALUES (%s, %s, %s)",
                    (id['DestID'], lat, lng))
        connection.commit()
        cur.close()

        ##TODO: figure out why this if statement isn't working... error is thrown if no tags input
        if tags != None:
            for tag in tags.split(','):
                cur = connection.cursor()

                cur.execute("SELECT TagID "
                            "FROM Tags "
                            "WHERE TagName = %s"
                            , [tag])
                tagId = cur.fetchone()
                
                cur.execute("INSERT INTO dest_tags "
                            "VALUES (%s, %s)"
                            , (id['DestID'], tagId['TagID']))
                connection.commit()
                cur.close()

        return redirect(url_for('destinations'))
            
    cur = connection.cursor()
    cur.execute("SELECT TagName FROM tags")
    tags = cur.fetchall()
    cur.close()

    tagsList = []
    for tag in tags:
        tagsList.append(tag['TagName'])

    return render_template('create_destination.html', form=form, tags=tagsList)

@app.route('/edit_destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_destination(id):
    cur = connection.cursor()

    cur.execute("SELECT d.DestID, DestName, CountryID, Category, Description, ImgUrl, Lat, Lng "
                "FROM destinations d JOIN dest_images i ON d.DestID = i.DestID "
                                    "JOIN dest_locations l ON d.DestID = l.DestID "
                "WHERE d.DestID = %s"
                , id)
    destination = cur.fetchone()

    cur.execute("SELECT t.TagName "
                "FROM tags t JOIN dest_tags dt ON t.TagID = dt.TagID "
                "WHERE dt.DestID = %s"
                , id)
    tags = cur.fetchall()

    cur.close()

    tagsList = []
    for tag in tags:
        tagsList.append(tag['TagName'])
    myTags = ','.join(tagsList)

    form = DestinationForm(request.form)

    form.name.data = destination['DestName']
    form.countryId.data = destination['CountryID']
    form.category.data = destination['Category']
    form.description.data = destination['Description']
    form.imgUrl.data = destination['ImgUrl']
    form.lat.data = destination['Lat']
    form.lng.data = destination['Lng']

    if request.method == 'POST':
        name = request.form['name']
        countryId = request.form['countryId']
        category = request.form['category']
        description = request.form['description']
        tags = request.form['tags']
        imgUrl = request.form['imgUrl']
        lat = request.form['lat']
        lng = request.form['lng']

        cur = connection.cursor()
        cur.execute("UPDATE destinations "
                    "SET DestName=%s, CountryID=%s, Category=%s, Description=%s "
                    "WHERE DestID=%s"
                    , (name, countryId, category, description, id))

        cur.execute("UPDATE dest_images "
                    "SET ImgURL = %s "
                    "WHERE DestID=%s"
                    , (imgUrl, id))
        
        cur.execute("UPDATE dest_locations "
                    "SET Lat=%s, Lng= %s "
                    "WHERE DestID=%s"
                    , (lat, lng, id))

        connection.commit()
        cur.close()

        # Deletes all existing tags, then adds the current ones back.
        cur = connection.cursor()
        cur.execute("DELETE "
                    "FROM dest_tags "
                    "WHERE DestID = %s"
                    , id)
        connection.commit()
        cur.close()

        for tag in tags.split(','):
            cur = connection.cursor()

            cur.execute("SELECT TagID "
                        "FROM Tags "
                        "WHERE TagName = %s"
                        , [tag])
            tagId = cur.fetchone()
            
            cur.execute("INSERT INTO dest_tags "
                        "VALUES (%s, %s)"
                        , (id, tagId['TagID']))
            connection.commit()
            cur.close()
        
        return redirect(url_for('destinations'))

    cur = connection.cursor()
    cur.execute("SELECT TagName FROM tags")
    tags = cur.fetchall()
    cur.close()

    allTags = []
    for tag in tags:
        allTags.append(tag['TagName'])

    return render_template('edit_destination.html', form=form, allTags=allTags, myTags=myTags)


@app.route('/alter-explored', methods=['POST'])
def alter_explored():
    id = request.form['id']
    action = request.form['action']
    
    cur = connection.cursor()

    if action == "add":
        cur.execute("INSERT INTO explored "
                    "VALUES (%s, %s)"
                    , (session['user'], id))
    elif action == "remove":
        cur.execute("DELETE FROM explored "
                    "WHERE UserID = %s AND DestID = %s"
                    , (session['user'], id))  

    connection.commit()
    cur.close()
    return "success"

@app.route('/alter-favorite', methods=['POST'])
def alter_favorite():
    id = request.form['id']
    action = request.form['action']
    
    cur = connection.cursor()

    if action == "add":
        cur.execute("INSERT INTO favorites "
                    "VALUES (%s, %s)"
                    , (session['user'], id))
    elif action == "remove":
        cur.execute("DELETE FROM favorites "
                    "WHERE UserID = %s AND DestID = %s"
                    , (session['user'], id))  

    connection.commit()
    cur.close()
    return "success"

if __name__ == '__main__':
    app.secret_key=os.environ['SECRET_KEY']
    app.run(debug=True, port=8000)
