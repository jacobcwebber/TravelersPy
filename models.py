from app import db
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=0)
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, email, password, is_admin, time_created):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.time_created = time_created

    def __repr__(self):
        return '<User ID: {}>'.format(self.user_id)

class Destination(db.Model):

class Country(db.Model):

class Region(db.Model):

class Continent(db.Model):

class Dest_Location(db.Model):

class Dest_Image(db.Model):

class Dest_Tags(db.Model):

class Explored(db.Model):

class Favorites(db.Model):

class Tag(db.Model):




