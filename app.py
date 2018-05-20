from flask import Flask, request, render_template, url_for, logging, session, flash, redirect, Markup, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql.cursors
import psycopg2
from functools import wraps
import sys
import json
import os

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['is_admin'] == True:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized. Requires administrator access.', 'danger')
            return redirect(url_for('index'))
    return

#####################################################
#####          USER FUNCTIONALITY                ####
#####################################################

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
def explored(): 
    cur = connection.cursor()
    cur.execute('SELECT d.DestID, DestName, ImgUrl '
                'FROM explored e JOIN destinations d ON e.DestID = d.DestID '
                                'JOIN dest_images i ON d.DestID = i.DestID '
                'WHERE e.UserID = %s'
                , session['user'])
    explored = cur.fetchall()

    return render_template('explored.html', explored=explored)

#####################################################
#####            DESTINATIONS PAGES              ####
#####################################################

@app.route('/destinations')
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

@app.route('/destination/<string:id>', methods=['POST', 'GET'])
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

@app.route('/edit_destination/<string:id>', methods=['POST', 'GET'])
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
