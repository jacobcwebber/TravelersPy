from flask import Flask, request, render_template, url_for, logging, session, flash, redirect, Markup
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, FileField, ValidationError
from functools import wraps
import re
import sys
import json

app = Flask(__name__)

import travelers.destinations
import travelers.countries

connection = pymysql.connect(host='localhost',
                             user='Jacob',
                             password='691748jw',
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
        if session['admin'] == True:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized. Requires administrator access.', 'danger')
            return redirect(url_for('index'))
    return

@app.route('/')
def index():
    return render_template('home.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.secret_key='supersecretkey'
    app.run(port=8000, debug=True)
