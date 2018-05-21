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

#####################################################
#####            DESTINATIONS PAGES              ####
#####################################################

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
