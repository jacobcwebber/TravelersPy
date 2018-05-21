from app import app, db, login
from datetime import datetime
from time import time
import jwt
from flask_login import UserMixin
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

## Association tables

explored = db.Table('explored',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id'))
)

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id'))
)

dest_tags = db.Table('dest_tags',
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

## Model tables
        
class Continent(db.Model):
    __tablename__ = 'continents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    regions = db.relationship('Region', backref='continent', lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('continents.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(100), unique=True)
    countries = db.relationship('Country', backref='region', lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(100), unique=True)
    destinations = db.relationship('Destination', backref='country', lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    dest_location = db.relationship('Dest_Location', backref=backref("destination", uselist=False))
    dest_img = db.relationship('Dest_Image', backref=backref("destination", uselist=False))
    tags = db.relationship('Tag', secondary='dest_tags',
        backref=db.backref('destinations', lazy='dynamic'),
        lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

    def add_tag(self, tag):
        self.tags.append(tag)
    
    def remove_tag(self, tag):
        self.tags.remove(tag)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(140))
    is_admin = db.Column(db.Boolean, default=0)
    time_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    explored_dests = db.relationship(
        'Destination', secondary=explored,
        backref=db.backref('explored_users', lazy='dynamic'),
        lazy='dynamic')
    favorited_dests = db.relationship(
        'Destination', secondary=favorites,
        backref=db.backref('favorited_users', lazy='dynamic'),
        lazy='dynamic')

    def __repr__(self):
        return '<ID: {}, Name: {} {}>'.format(self.id, self.first_name, self.last_name)

    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='H256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['H256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def add_explored(self, dest):
        if not self.has_explored(dest):
            self.explored_dests.append(dest)
    
    def remove_explored(self, dest):
        if self.has_explored(dest):
            self.explored_dests.remove(dest)

    def has_explored(self, dest):
        return self.explored_dests.filter(
            explored.c.dest_id == dest.id).count() > 0

    def add_favorite(self, dest):
        if not self.has_favorited(dest):
            self.favorited_dests.append(dest)  

    def remove_favorite(self, dest):
        if self.has_favorited(dest):
            self.favorited_dests.remove(dest)

    def has_favorited(self, dest):    
        return self.favorited_dests.filter(
            favorites.c.dest_id == dest.id).count() > 0

    # def get_by_tag(self, tag):
    #     return self.explored_dests

class Dest_Location(db.Model):
    __tablename__ = 'dest_locations'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    lat = db.Column(db.Numeric(10,8))
    lng = db.Column(db.Numeric(11,8))

    def __repr__(self):
        return '<Dest ID: {}, Coordinates: ({}, {})>'.format(self.dest_id, self.lat, self.lng)

class Dest_Image(db.Model):
    __tablename__ = 'dest_images'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    img_url = db.Column(db.String(255))

    def __repr__(self):
        return '<Dest ID: {}, Image URL: {}>'.format(self.dest_id, self.img_url)
        
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __repr__(self):
        return '<{}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))