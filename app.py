#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import datetime
import json
from tkinter import PhotoImage
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_migrate import Migrate
import logging, sys
import psycopg2
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import models
from models import Venue, Artist, Show, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  
    areas = db.session.query(Venue.city, Venue.state).group_by(Venue.state, Venue.city).all()
    data = []
    
    for a in areas:
      id = db.session.query(Venue.id,Venue.name).filter(Venue.city==a[0],Venue.state==a[1]).all()
      data.append({"city":a[0], "state":a[1],"venues":[]})
      for v in id:
        data[-1]["venues"].append({"id":v[0], "name":v[1]})
    

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_venue = request.form['search_term']
  searches = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike(f"%{search_venue}%")).all()

  response = {
    "count": len(searches),
    "data": [{
      "id": id,
      "name": name
    } for id, name in searches]
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get_or_404(venue_id)

  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
      temp_show = {
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_time <= datetime.now():
          past_shows.append(temp_show)
      else:
          upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
    
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
# TODO: insert form data as a new Venue record in the db, instead
def create_venue_submission():
  error = False
  # form = VenueForm()
  form = VenueForm(request.form)
  
  try:
    venue = Venue(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data,
    genres = form.genres.data,
    website_link = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    )
    
    # print(venue.name)
    # # exit()
    db.session.add(venue)
    db.session.commit()  
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # TODO: modify data to be the data object returned from db insertion
    if error:
      flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # name = None
	# form = VenueForm()
  # venue_id = request.form.get('venue_id')
  venue_delete = db.session.query(Venue).filter(Venue.id == venue_id)
  # venue_name = venue_delete.name
  db.session.delete(venue_delete)
  db.session.commit()
  flash('Venue deleted successfully.')
  
  # venueshow = Venue.query.order_by(Venue.id)
  # return redirect(url_for('show_venue', form=form, venue_id=venue_id))
  return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = db.session.query(Artist.id, Artist.name).group_by(Artist.id, Artist.name).all()
    
      
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_artists = request.form['search_term']
  searches = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(f"%{search_artists}%")).all()

  response = {
    "count": len(searches),
    "data": [{
      "id": id,
      "name": name 
      }
    for id, name in searches]
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get_or_404(artist_id)

  past_shows = []
  upcoming_shows = []

  for show in artist.shows:
      temp_show = {
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_time <= datetime.now():
          past_shows.append(temp_show)
      else:
          upcoming_shows.append(temp_show)

  data = vars(artist)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>
  get_artist = Artist.query.get(artist_id)
  data={
    "id": get_artist.id,
    "name": get_artist.name,
    "genres": get_artist.genres,
    "city": get_artist.city,
    "state": get_artist.state,
    "phone": get_artist.phone,
    "website_link": get_artist.website_link,
    "facebook_link": get_artist.facebook_link,
    "seeking_venue": get_artist.seeking_venue,
    "seeking_description": get_artist.seeking_description,
    "image_link": get_artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  update_artist = Artist.query.get(artist_id)
  
  if request.method == 'POST':
    update_artist.name  = request.form['name']
    update_artist.genres = request.form.getlist('genres')
    update_artist.city =  request.form['city']
    update_artist.state = request.form['state']
    update_artist.phone = request.form['phone']
    update_artist.website_link = request.form['website_link']
    update_artist.facebook_link = request.form['facebook_link']
    update_artist.seeking_venue = request.form['seeking_venue']
    update_artist.seeking_description = request.form['seeking_description']
    update_artist.image_link = request.form['image_link']
    try:
      db.session.commit()
      flash('The Artist was updated successfully.')
      return redirect(url_for('show_artist', form=form, artist_id=artist_id))
    except:
      flash('An error occured when updating the Artist .')
      return redirect(url_for('show_artist', form=form, artist_id=artist_id))
  else:
      return redirect(url_for('show_artist', form=form, artist_id=artist_id))
    
    

  
  
    # return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TODO: populate form with values from venue with ID <venue_id>
  get_venue = Venue.query.get(venue_id)
  data={
    "id": get_venue.id,
    "name": get_venue.name,
    "genres": get_venue.genres,
    "address": get_venue.address,
    "city": get_venue.city,
    "state": get_venue.state,
    "phone": get_venue.phone,
    "website_link": get_venue.website_link,
    "facebook_link": get_venue.facebook_link,
    "seeking_talent": get_venue.seeking_talent,
    "seeking_description": get_venue.seeking_description,
    "image_link": get_venue.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  update_venue = Venue.query.get(venue_id)
  
  if request.method == 'POST':
    update_venue.name  = request.form['name']
    update_venue.genres = request.form.getlist('genres')
    update_venue.address = request.form['address']
    update_venue.city =  request.form['city']
    update_venue.state = request.form['state']
    update_venue.phone = request.form['phone']
    update_venue.website_link = request.form['website_link']
    update_venue.facebook_link = request.form['facebook_link']
    update_venue.seeking_talent = request.form['seeking_talent']
    update_venue.seeking_description = request.form['seeking_description']
    update_venue.image_link = request.form['image_link']
    # try:
    db.session.commit()
    flash('The Venue was updated successfully.')
    return redirect(url_for('show_venue', venue_id=venue_id))
    # except:
    flash('An error occured when updating the Venue. ')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
      return redirect(url_for('show_venue', venue_id=venue_id))
  # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  form = ArtistForm(request.form)
  try:
    artist = Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website_link = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
    )
  
    db.session.add(artist)
    db.session.commit()

  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    # db.session.close()
    if error:
      flash('An error occurred. Artist ' +  request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  get_show = db.session.query(Show)
  show_tuple = []
  
  for a in get_show:
    show_tuple.append({"venue_id":a.venue_id,"venue_name":a.venue.name,"artist_id":a.artist_id,"artist_name":a.artist.name,"artist_image_link":a.artist.image_link,"start_time":str(a.start_time)})
    
    
    return render_template('pages/shows.html', shows=show_tuple)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form)
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
  
    db.session.add(show)
    db.session.commit()

  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    # db.session.close()
    if error:
      flash('Error in listing a new show')
    else:
      flash('A new show has been listed successfully')
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
