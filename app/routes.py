from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User,  Destination, Country, Dest_Location, Tag
from datetime import datetime
import sys

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    registration_form = RegistrationForm()

    if registration_form.validate_on_submit() and registration_form.register.data:
        user = User(first_name=registration_form.first_name.data, 
                    last_name=registration_form.last_name.data, 
                    email=registration_form.email.data)
        user.set_password(registration_form.password.data)
        db.session.add(user)
        db.session.commit() 
        return redirect(url_for('login'))

    if login_form.validate_on_submit() and login_form.login.data:
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid email or password.')
            return redirect(url_for('login'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('index.html', login_form=login_form, registration_form=registration_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()

    if login_form.validate_on_submit() and login_form.login.data:
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid email or password.')
            return redirect(url_for('login'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', login_form=login_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    recent = Destination.query.first()
    print(recent.img_url, file=sys.stderr)
    # cur = connection.cursor()
    # cur.execute("SELECT d.DestID, DestName, ImgUrl "
    #             "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
    #             "ORDER BY d.UpdateDate DESC")
    # recent = cur.fetchall()

    # cur.execute("SELECT d.DestID, d.DestName, i.ImgUrl, count(f.DestID) AS Favorites "
    #             "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
    #                                 "JOIN favorites f on d.destID = f.DestID "
    #             "GROUP BY f.DestID "
    #             "ORDER BY Favorites DESC")
    # popular = cur.fetchall()

    # cur.execute("SELECT DestID "
    #             "FROM favorites "
    #             "WHERE UserID = %s"
    #             , session['user'])
    # favs = cur.fetchall()

    # cur.execute("SELECT DestID "
    #             "FROM explored "
    #             "WHERE UserID = %s"
    #             , session['user'])
    # exp = cur.fetchall()
    # cur.close()

    # favorites = []
    # for dest in favs:
    #     favorites.append(dest['DestID'])

    # explored = []
    # for dest in exp:
    #     explored.append(dest['DestID'])

    # cur = connection.cursor()
    # cur.execute("SELECT COUNT(*) AS Count "
    #             "FROM Destinations")
    # count = cur.fetchone()

    return render_template('home.html', recent=recent)

@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    favorites = user.favorited_dests.all()
    explored = user.explored_dests.all()

    # cur.execute("SELECT c.CountryID "
    #             "FROM explored e JOIN destinations d ON e.DestID = d.DestID JOIN countries c ON d.CountryID = c.CountryID "
    #             "WHERE e.UserID = %s "
    #             "GROUP BY c.CountryID"
    #             , session['user'])
    # countries = cur.fetchall()

    # cur.execute("SELECT d.DestID "
    #             "FROM explored e JOIN destinations d ON e.DestID = d.DestID "
    #                             "JOIN dest_tags dt ON  dt.DestID = d.DestID "
    #                             "JOIN tags t ON t.TagID = dt.TagID "
    #             "WHERE e.UserID = %s AND t.TagName = 'UNESCO'"
    #             , session['user'])
    # unesco = cur.fetchall()

    # cur.execute("SELECT l.Lat, l.Lng, d.DestName "
    #             "FROM dest_locations l JOIN destinations d on l.DestID = d.DestID")
    # locations = cur.fetchall()
    # cur.close()
    
    # locationsList = []
    # for location in locations:
    #     locationsList.append([float(location['Lat']), float(location['Lng']), location['DestName']])

    counts = [25, 100, 30, 15]
    captions = ['Explored', 'Favorites', 'Countries Visited', 'UNESCO Sites Visited']


    return render_template('user.html', user=user, counts=counts, captions=captions)



