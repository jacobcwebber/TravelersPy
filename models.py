from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=0)
    time_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id, email, password_hash, is_admin, time_created):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.time_created = time_created

    def __repr__(self):
        return '<User ID: {}>'.format(self.user_id)

class Continent(db.Model):
    __tablename__ = 'continents'

    cont_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cont_name = db.Column(db.String(100), unique=True, nullable=False)
    regions = db.relationship('Region', backref='continent', lazy='dynamic')

    def __init__(self, cont_id, cont_name):
        self.cont_id = cont_id
        self.cont_name = cont_name

    def __repr__(self):
        return '<{}>'.format(self.cont_name)

class Region(db.Model):
    __tablename__ = 'regions'

    region_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('continents.cont_id', onupdate="CASCADE", ondelete="CASCADE"))
    region_name = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, region_id, cont_id, region_name):
        self.region_id = region_id
        self.cont_id = cont_id
        self.region_name = region_name

    def __repr__(self):
        return '<{}>'.format(self.region_name)

class Country(db.Model):
    __tablename__ = 'countries'

    country_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id', onupdate="CASCADE", ondelete="CASCADE"))
    country_name = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, country_id, region_id, country_name, update_date):
        self.country_id = country_id
        self.region_id = region_id
        self.country_name = country_name

    def __repr__(self):
        return '<{}>'.format(self.country_name)

class Destination(db.Model):
    __tablename__ = 'destinations'

    dest_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.country_id', onupdate="CASCADE", ondelete="CASCADE"))
    dest_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    update_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow())

    def __init__(self, dest_id, country_id, dest_name, description, update_date):
        self.dest_id = dest_id
        self.country_id = country_id
        self.dest_name = dest_name
        self.description = description
        self.update_date = update_date

    def __repr__(self):
        return '<{}>'.format(self.dest_name)    

class Dest_Location(db.Model):
    __tablename__ = 'dest_locations'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.dest_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    lat = db.Column(db.Numeric(10,8), nullable=False)
    lng = db.Column(db.Numeric(11,8), nullable=False)

    def __init__(self, dest_id, lat, lng):
        self.dest_id = dest_id
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return '<Destination ID: {}, Coordinates: {}, {}>'.format(self.dest_id, self.lat, self.lng)

class Dest_Image(db.Model):
    __tablename__ = 'dest_images'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.dest_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    img_url = db.Column(db.String(255), primary_key=True)

    def __init__(self, dest_id, img_url):
        self.dest_id = dest_id
        self.img_url = img_url

    def __repr__(self):
        return '<Destination ID: {}, Image URL: {}>'.format(self.dest_id, self.img_url)
        
class Tag(db.Model):
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(255), nullable=False)

    def __init__(self, tag_id, tag_name):
        self.tag_id = tag_id
        self.tag_name = tag_name

    def __repr__(self):
        return '<{}>'.format(self.tag_name)


class Dest_Tags(db.Model):
    __tablename__ = 'dest_tags'

    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.dest_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)

    def __init__(self, dest_id, tag_id):
        self.dest_id = dest_id
        self.tag_id = tag_id

    def __repr__(self):
        return '<Destination ID: {}, Tag ID: {}>'.format(self.dest_id, self.tag_id)

class Explored(db.Model):
    __tablename__ = 'explored'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.dest_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)

    def __init__(self, user_id, dest_id):
        self.user_id = user_id
        self.dest_id = dest_id

    def __repr__(self):
        return '<User ID: {}, Explored Dest ID: {}>'.format(self.user_id, self.dest_id)

class Favorites(db.Model):
    __tablename__ = 'favorites'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    dest_id = db.Column(db.Integer, db.ForeignKey('destinations.dest_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)

    def __init__(self, user_id, dest_id):
        self.user_id = user_id
        self.dest_id = dest_id

    def __repr__(self):
        return '<User ID: {}, Favorite Dest ID: {}>'.format(self.user_id, self.dest_id)



