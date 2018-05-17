from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

## Association tables

explored = db.Table('explored',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id'), nullable=False)
)

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id'), nullable=False)
)

dest_tags = db.Table('dest_tags',
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id'), nullable=False),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), nullable=False)
)

## Model tables

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=0)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    explored_dests = db.relationship(
        'Destination', secondary=explored,
        backref=db.backref('users_explored', lazy='dynamic'))
    favorited_dests = db.relationship(
        'Destination', secondary=favorites,
        backref=db.backref('users_favorited', lazy='dynamic') )

    def __repr__(self):
        return '<ID: {}, Username: {}>'.format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def add_explored(self, dest):
        if not self.has_explored(dest):
            self.explored_dests.append(dest)
    
    def remove_explored(self, dest):
        if self.has_explored(dest):
            self.explored_dests.remove(dest)

    def has_explored(self, dest):
        return self.explored_dests.filter(
            users_explored.c.dest_id == dest.id).count() > 0

    def add_favorite(self, dest):
        if not self.has_favorited(dest):
            self.favorited_dests.append(dest)  

    def remove_favorite(self, dest):
        if self.has_favorited(dest):
            self.favorited_dests.remove(dest)

    def has_favorited(self, dest):    
        return self.favorited_dests.filter(
            users_favorited.c.dest_id == dest.id).count() > 0
        
class Continent(db.Model):
    __tablename__ = 'continents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    regions = db.relationship('Region', backref='continent', lazy='dynamic')

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<{}>'.format(self.name)

class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('continents.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, id, cont_id, name):
        self.id = id
        self.cont_id = cont_id
        self.name = region_name

    def __repr__(self):
        return '<{}>'.format(self.name)

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, id, region_id, name, update_date):
        self.id = id
        self.region_id = region_id
        self.name = name

    def __repr__(self):
        return '<{}>'.format(self.name)

class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    tags = db.relationship('Tag', secondary='dest_tags',
        backref=db.backref('destinations', lazy='dynamic'))

    def __init__(self, id, country_id, name, description, update_date):
        self.id = id
        self.country_id = country_id
        self.name = name
        self.description = description
        self.update_date = update_date

    def __repr__(self):
        return '<{}>'.format(self.name)    

class Dest_Location(db.Model):
    __tablename__ = 'dest_locations'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    lat = db.Column(db.Numeric(10,8), nullable=False)
    lng = db.Column(db.Numeric(11,8), nullable=False)

    def __init__(self, dest_id, lat, lng):
        self.dest_id = dest_id
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return '<Dest ID: {}, Coordinates: ({}, {})>'.format(self.dest_id, self.lat, self.lng)

class Dest_Image(db.Model):
    __tablename__ = 'dest_images'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    img_url = db.Column(db.String(255), primary_key=True)

    def __init__(self, dest_id, img_url):
        self.dest_id = dest_id
        self.img_url = img_url

    def __repr__(self):
        return '<Dest ID: {}, Image URL: {}>'.format(self.dest_id, self.img_url)
        
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<{}>'.format(self.name)



