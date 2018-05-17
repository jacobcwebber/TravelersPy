from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User,  Destination, Favorite, Explored, Country, Dest_Location, Dest_Tag, Tag
from datetime import datetime

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_to('destinations'))
    login_form = LoginForm()
    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    elif login_form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('index.html', login_form=login_form, registration_form=registration_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/user/<user_id>')
@login_required
def user(user_id):
    user = User.query.filter_by(user_id=user_id).first_or_404()
    favorites = 

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


    return render_template('user.html', user=user)



