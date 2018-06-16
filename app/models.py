from app import db, login
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.orm import backref
import jwt
from datetime import datetime
from hashlib import md5
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

explored = db.Table('explored',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE"))
)

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE"))
)

dest_tags = db.Table('dest_tags',
    db.Column('dest_id', db.Integer, db.ForeignKey('destinations.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', onupdate="CASCADE", ondelete="CASCADE"))
)
       
class Continent(db.Model):
    __tablename__ = 'continents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    regions = db.relationship('Region', backref='continent', lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('continents.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64), unique=True)
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
    name = db.Column(db.String(64), unique=True)
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
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(140))
    is_admin = db.Column(db.Boolean, default=0)
    time_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    explored_dests = db.relationship(
        'Destination', secondary=explored,
        backref=db.backref('explored_users', lazy='dynamic'),
        lazy='dynamic')
    favorited_dests = db.relationship(
        'Destination', secondary=favorites,
        backref=db.backref('favorited_users', lazy='dynamic'),
        lazy='dynamic')

    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def avatar(self, size):
        """Generate user gravatar."""

        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=604800):
        """Generate a confirmation token to email a new user."""

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        """Generate an email change token to email an existing user."""

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def generate_reset_password_token(self, expires_in=3600):
        """Generate a password reset change token to email to an existing user."""

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def confirm_account(self, token):
        """Verify that the provided token is correct for this user's id."""

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def reset_password(self, token, new_password):
        """Verify the new password for this user."""

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def alter_explored(self, dest):
        """Add or remove destinations from user's Explored"""

        if not self.has_explored(dest):
            self.explored_dests.append(dest)
        else:
            self.explored_dests.remove(dest)
    
    def has_explored(self, dest):
        return self.explored_dests.filter(
            explored.c.dest_id == dest.id).count() > 0

    def alter_favorite(self, dest):
        """Add or remove destinations from user's Favorites"""

        if not self.has_favorited(dest):
            self.favorited_dests.append(dest)  
        else: 
            self.favorited_dests.remove(dest)

    def has_favorited(self, dest):    
        return self.favorited_dests.filter(
            favorites.c.dest_id == dest.id).count() > 0

    def __repr__(self):
        return '<{} {}>'.format(self.first_name, self.last_name)

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