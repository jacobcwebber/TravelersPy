from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, func
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User,  Destination, Country, Dest_Location, Dest_Image, Tag, favorites
from app.email import send_password_reset_email
from datetime import datetime

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
    recent = Destination.query.join(Dest_Image)\
                        .add_columns(Destination.id, Destination.name, Destination.update_date, Dest_Image.img_url)\
                        .order_by(desc(Destination.update_date))\
                        .all()
    # popular = Destination.query.join(Dest_Image).join(favorites)\
    #                     .add_columns(Destination.id, Destination.name, Destination.update_date, Dest_Image.img_url)\
    #                     .group_by(favorites.dest_id)\
    #                     .order_by(desc(Destination.update_date))\
    #                     .all()
    explored = current_user.explored_dests.all()
    favs = current_user.favorited_dests.all()
    count = Destination.query.count()
    # cur.execute("SELECT d.DestID, d.DestName, i.ImgUrl, count(f.DestID) AS Favorites "
    #             "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
    #                                 "JOIN favorites f on d.destID = f.DestID "
    #             "GROUP BY f.DestID "
    #             "ORDER BY Favorites DESC")
    # popular = cur.fetchall()

    return render_template('home.html', recent=recent, explored=explored, favs=favs, count=count)

@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()

    favorites = user.favorited_dests.all()
    explored = user.explored_dests.all()
    countries = Countries.query.join(Destination).join()
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


@app.route('/search')
def search():
    location = request.args.get('location')
    keyword = request.args.get('keywords')

    # cur = connection.cursor()
    # if location:
    #     if keyword:
    #         cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl, ContName '
    #                     'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
    #                                         'JOIN countries c ON c.CountryID = d.CountryID '
    #                                         'JOIN regions r ON c.RegionID = r.RegionID '
    #                                         'JOIN continents co ON co.ContID = r.ContID '
    #                                         'JOIN dest_tags dt ON dt.DestID = d.DestID '
    #                                         'JOIN tags t ON dt.TagID = t.TagID '
    #                     'WHERE (c.CountryName = %s OR ContName = %s OR r.RegionName = %s) AND t.TagName = %s '
    #         , (location, location, location, keyword)) 
    #     else:
    #         cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl, ContName '
    #                     'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
    #                                         'JOIN countries c ON c.CountryID = d.CountryID '
    #                                         'JOIN regions r ON c.RegionID = r.RegionID '
    #                                         'JOIN continents co ON co.ContID = r.ContID '
    #                     'WHERE (c.CountryName = %s or ContName = %s OR r.RegionName = %s)'
    #         , (location, location, location))
    # elif keyword:
    #     cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl, ContName '
    #                 'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
    #                                     'JOIN countries c ON c.CountryID = d.CountryID '
    #                                     'JOIN regions r ON c.RegionID = r.RegionID '
    #                                     'JOIN continents co ON co.ContID = r.ContID '
    #                                     'JOIN dest_tags dt ON dt.DestID = d.DestID '
    #                                     'JOIN tags t on dt.TagID = t.TagID '
    #                 'WHERE t.TagName = %s'
    #     , keyword)   
    # else:
    #     cur.execute('SELECT d.DestID, DestName, c.CountryName, ImgUrl    '
    #                 'FROM destinations d JOIN dest_images i ON d.DestID = i.DestID '
    #                                     'JOIN countries c ON c.CountryID = d.CountryID '
    #                 'ORDER BY RAND() '
    #                 'LIMIT 5 '
    #             )
    # destinations = cur.fetchall()

    # # Add list of tags to the dictionaries for each destination
    # for dest in destinations:
    #     cur.execute('SELECT TagName '
    #                 'FROM vTags '
    #                 'WHERE DestName = %s'
    #                 , dest['DestName'])
    #     tags = cur.fetchall()

    #     tagsList = [tag['TagName'] for tag in tags]
    #     dest['Tags'] = tagsList

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

    # favorites = [dest['DestID'] for dest in favs]
    # explored = [dest['DestID'] for dest in exp]

    # cur.execute('SELECT TagName FROM tags')
    # tags = cur.fetchall()

    # cur.execute('SELECT CountryName FROM countries')
    # countries = cur.fetchall()

    # cur.execute('SELECT ContName FROM continents')
    # continents = cur.fetchall()

    # cur.execute('SELECT RegionName FROM regions')
    # regions = cur.fetchall()
    # cur.close()

    # countriesList = [country['CountryName'] for country in countries]
    # continentsList = [continent['ContName'] for continent in continents]
    # regionsList = [region['RegionName'] for region in regions]
    # tagsList = [tag['TagName'] for tag in tags]

    # locationsList = list(set(countriesList).union(set(list(set(continentsList).union(set(regionsList))))))
    
    return render_template('search.html')


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



