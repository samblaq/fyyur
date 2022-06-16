from flask_sqlalchemy import SQLAlchemy
# from flask import Flask
# from flask_moment import Moment
# from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    website_link = db.Column(db.String(500), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False,nullable=True)
    seeking_description = db.Column(db.String(500),nullable=True)
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")
    
    
    def __repr__(self):
      return f'<Venue ID={self.id} Name={self.name}>'
    
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.String, nullable=False)
    seeking_description = db.Column(db.String(500),nullable=True)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")
    
    def __repr__(self):
      return f'<Artist ID:{self.id} Name:{self.name}>'    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  # upcoming = db.Column(db.Boolean, nullable=False, default=False)