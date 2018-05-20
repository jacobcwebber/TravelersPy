from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, func, text
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User,  Destination, Country, Region, Continent, Dest_Location, Dest_Image, Tag
from app.email import send_password_reset_email
from app.tools import execute
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
    return render_template('login.html', title="Wanderlist | Login", login_form=login_form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    recent_query = text('SELECT d.id, d.name, d.update_date, i.img_url '
                        'FROM destinations d JOIN dest_images i on d.id = i.dest_id '
                        'ORDER BY d.update_date DESC')
    popular_query = text('SELECT d.id, d.name, i.img_url, count(f.dest_id) as favorites '
                        'FROM destinations d JOIN dest_images i ON d.id = i.dest_id '
                                            'JOIN favorites f ON d.id = f.dest_id '
                        'GROUP BY d.id, i.img_url '
                        'ORDER BY favorites DESC')
    recent = execute(recent_query)
    popular = execute(popular_query)
    explored = [dest.id for dest in current_user.explored_dests.all()]
    favorites = [dest.id for dest in current_user.favorited_dests.all()]
    dest_count = Destination.query.count()

    return render_template('home.html', recent=recent, popular=popular, explored=explored, favorites=favorites, dest_count=dest_count)

@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()

    favorites = user.favorited_dests.all()
    explored = user.explored_dests.all()
    dests = Destination.query.all()
    print(dests, file=sys.stderr)
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


    return render_template('user.html', title=user.first_name + ' ' + user.last_name, user=user, counts=counts, captions=captions)


@app.route('/search')
def search():
    location = request.args.get('location')
    keyword = request.args.get('keywords')

    base = 'SELECT d.id, d.name as name, c.name as country, i.img_url, co.name as cont '\
           'FROM destinations d JOIN dest_images i ON d.id = i.dest_id '\
                               'JOIN countries c ON d.country_id = c.id '\
                               'JOIN regions r ON c.region_id = r.id '\
                               'JOIN continents co ON r.cont_id = co.id '\
                               'JOIN dest_tags dt ON dt.dest_id = d.id '\
                               'JOIN tags t ON dt.tag_id = t.id '

    if location:
        if keyword:
            where = 'WHERE (c.CountryName = {} OR ContName = {} OR r.RegionName = {}) AND t.TagName = {}'\
                    .format(location, location, location, keyword)
        else:
            where = 'WHERE (c.CountryName ={} or ContName = {} OR r.RegionName = {})'\
            .format(location, location, location)
    elif keyword:
        where = 'WHERE t.TagName = {}'.format(keyword)
    else:
        where = 'ORDER BY random() LIMIT 5 '
    query = text(base + where)
    dests = execute(query)

    for dest in dests:
        d = Destination.query.get(dest['id'])
        dest['Tags'] = [tag.name for tag in d.tags.all()]

    explored = [dest.id for dest in current_user.explored_dests.all()]
    favorites = [dest.id for dest in current_user.favorited_dests.all()]

    countries = [country.name for country in Country.query.all()]
    continents = [continent.name for continent in Continent.query.all()]
    regions = [region.name for region in Region.query.all()]
    locations = list(set(countries).union(set(list(set(continents).union(set(regions))))))

    tags = [tag.name for tag in Tag.query.all()]

    return render_template('search.html', dests=dests, locations=locations, tags=tags, explored=explored, favorites=favorites)    


@app.route('/create-destination', methods=['POST', 'GET'])
def create_destination():
    # form = DestinationForm(request.form)
    # if request.method == 'POST' and form.validate():
    #     name = form.name.data
    #     countryId = form.countryId.data
    #     category = form.category.data
    #     description = form.description.data
    #     imgUrl = form.imgUrl.data
    #     tags = form.tags.data
    #     lat = form.lat.data
    #     lng = form.lng.data

    #     cur = connection.cursor()

    #     cur.execute("INSERT INTO destinations(DestName, CountryID, Category, Description) "
    #                 " VALUES (%s, %s, %s, %s)"
    #                 , (name, countryId, category, description))

    #     connection.commit()
    #     cur.close()

    #     cur = connection.cursor()

    #     cur.execute("SELECT DestID "
    #                 "FROM destinations "
    #                 "WHERE DestName = %s"
    #                 , [name])
    #     id = cur.fetchone()

    #     cur.execute("INSERT INTO dest_images "
    #                 " VALUES (%s, %s)",
    #                 (id['DestID'], imgUrl))
    #     connection.commit()

    #     cur.execute("INSERT INTO dest_locations "
    #                 " VALUES (%s, %s, %s)",
    #                 (id['DestID'], lat, lng))
    #     connection.commit()
    #     cur.close()

    #     ##TODO: figure out why this if statement isn't working... error is thrown if no tags input
    #     if tags != None:
    #         for tag in tags.split(','):
    #             cur = connection.cursor()

    #             cur.execute("SELECT TagID "
    #                         "FROM Tags "
    #                         "WHERE TagName = %s"
    #                         , [tag])
    #             tagId = cur.fetchone()
                
    #             cur.execute("INSERT INTO dest_tags "
    #                         "VALUES (%s, %s)"
    #                         , (id['DestID'], tagId['TagID']))
    #             connection.commit()
    #             cur.close()

    #     return redirect(url_for('destinations'))
            
    # cur = connection.cursor()
    # cur.execute("SELECT TagName FROM tags")
    # tags = cur.fetchall()
    # cur.close()

    # tagsList = []
    # for tag in tags:
    #     tagsList.append(tag['TagName'])

    return render_template('create_destination.html', form=form, tags=tagsList)

@app.route('/alter-explored', methods=['POST'])
def alter_explored():
    dest = Destination.query.get(request.form['id'])
    action = request.form['action']
    
    if action == "add":
        current_user.add_explored(dest)
    elif action == "remove":
        current_user.remove_explored(dest)
    db.session.commit()

    return "success"

@app.route('/alter-favorite', methods=['POST'])
def alter_favorite():
    dest = Destination.query.get(request.form['id'])
    action = request.form['action']
    
    if action == "add":
        current_user.add_favorite(dest)
    elif action == "remove":
        current_user.remove_favorite(dest)
    db.session.commit()

    return "success"



