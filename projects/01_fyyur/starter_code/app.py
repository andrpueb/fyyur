#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
from models import app, db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database DONE: Connection added in the config object




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

def venue_shows(id):
  shows_list = {}
  past_shows = []
  upcoming_shows = []
  all_venue_shows = Show.query.filter_by(venue_id=id).all()
  for show in all_venue_shows:
    start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    artist = Artist.query.get(show.artist_id)
    if start_time > datetime.now():
      data = {}
      data["artist_id"]= artist.id
      data["artist_name"] = artist.name
      data["artist_image_link"]= artist.image_link
      data["start_time"] = show.start_time
      upcoming_shows.append(data)
    else:
      data = {}
      data["artist_id"] = artist.id
      data["artist_name"] = artist.name
      data["artist_image_link"]= artist.image_link
      data["start_time"] = show.start_time
      past_shows.append(data)
  shows_list['past_shows'] = past_shows
  shows_list['upcoming_shows'] = upcoming_shows
  return shows_list


@app.route('/venues')
def venues():
  venues = Venue.query.order_by('id').all()
  areas = []
  unique_areas = []
  for venue in venues:
    the_city = {}
    the_city['city'] = venue.city
    the_city['state'] = venue.state
    unique = venue.city +'-'+ venue.state
    if unique not in unique_areas:
      unique_areas.append(unique)
      venues = []
      city_venues = Venue.query.filter_by(city=venue.city).all()
      for venue in city_venues:
        the_venue = {}
        the_venue['id'] = venue.id
        the_venue['name'] = venue.name
        the_venue['num_upcoming_shows'] = len(venue_shows(venue.id)['upcoming_shows'])
        venues.append(the_venue)
      the_city['venues'] = venues
      areas.append(the_city)
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  response = {}
  if len(venues) > 0:
    response["count"] = len(venues)
    data = []
    for venue in venues:
      the_venue = {}
      the_venue["id"] = venue.id
      the_venue["name"] = venue.name
      the_venue['num_upcoming_shows'] = len(venue_shows(venue.id)['upcoming_shows'])
      data.append(the_venue)
    response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  venue.genres = venue.genres.split(',')
  past_shows = venue_shows(venue.id)['past_shows']
  upcoming_shows = venue_shows(venue.id)['upcoming_shows']
  venue.past_shows = past_shows
  venue.upcoming_shows = upcoming_shows
  venue.past_shows_count = len(past_shows)
  venue.upcoming_shows_count = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:    
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    genres = ','.join(request.form.getlist('genres'))
    phone = request.form['phone']
    website = request.form['website']
    facebook_link  = request.form['facebook_link']
    seeking_talent = True if request.form['seeking_talent'] else False
    seeking_description = request.form['seeking_talent']
    image_link = request.form['image_link']
    new_venue = Venue(name=name, city=city, state=state, address=address, genres=genres, phone=phone, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description, facebook_link=facebook_link, image_link=image_link)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  if not error:
    flash('Venue ' + name + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  body = {}
  error = False
  confirm = request.get_json()['confirm_id']
  try:
    if(confirm == venue_id):
      delete_venue = Venue.query.get(venue_id)
      db.session.delete(delete_venue)
      db.session.commit()
      body['result'] = 'deleted'
      flash('The venue was succesfully deleted!')
    else:
      body['result'] = 'not deleted'
      flash('The confirmation id is not correct, the venue has not been deleted')
  except: 
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  if not error:
    return jsonify(body)

#  Artists
#  ----------------------------------------------------------------
def artist_shows(id):
  shows_list = {}
  past_shows = []
  upcoming_shows = []
  all_artist_shows = Show.query.filter_by(artist_id=id).all()
  for show in all_artist_shows:
    start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    venue = Venue.query.get(show.venue_id)
    if start_time > datetime.now():
      data = {}
      data["venue_id"] = venue.id
      data["venue_name"] = venue.name
      data["venue_image_link"]= venue.image_link
      data["start_time"] = show.start_time
      upcoming_shows.append(data)
    else:
      data = {}
      data["venue_id"] = venue.id
      data["venue_name"] = venue.name
      data["venue_image_link"]= venue.image_link
      data["start_time"] = show.start_time
      past_shows.append(data)
  shows_list['past_shows'] = past_shows
  shows_list['upcoming_shows'] = upcoming_shows
  return shows_list


@app.route('/artists')
def artists():
  artists = Artist.query.order_by('id').all()
  data = []
  for artist in artists:
    artist_info = {}
    artist_info['id'] = artist.id
    artist_info['name'] = artist.name
    artist_info['num_upcoming_shows'] = len(artist_shows(artist.id)['upcoming_shows'])
    data.append(artist_info)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response = {}
  if len(artists) > 0:
    response['count'] = len(artists)
    data = []
    for artist in artists:
      the_artist = {}
      the_artist['id'] = artist.id
      the_artist['name'] = artist.name
      the_artist['num_upcoming_shows'] = len(artist_shows(artist.id)['upcoming_shows'])
      data.append(the_artist)
    response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist.genres = artist.genres.split(',')
  past_shows = artist_shows(artist.id)['past_shows']
  upcoming_shows = artist_shows(artist.id)['upcoming_shows']
  artist.upcoming_shows = upcoming_shows
  artist.past_shows = past_shows
  artist.past_shows_count = len(past_shows)
  artist.upcoming_shows_count = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    name = request.form['name']
    genres = ','.join(request.form.getlist('genres'))
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = True if request.form['seeking_venue'] else False
    seeking_description = request.form['seeking_venue']
    image_link = request.form['image_link']
    db.session.query(Artist).filter(Artist.id == artist_id).update({'name':name, 'genres':genres, 'city':city, 'state':state, 'phone':phone, 'website':website, 'facebook_link':facebook_link, 'seeking_venue':seeking_venue, 'seeking_description': seeking_description, 'image_link': image_link}) 
    db.session.commit()
    flash('The Artist was succesfully edited')
  except:
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    genres = ','.join(request.form.getlist('genres'))
    phone = request.form['phone']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = True if request.form['seeking_talent'] else False
    seeking_description = request.form['seeking_talent']
    image_link = request.form['image_link']
    db.session.query(Venue).filter(Venue.id == venue_id).update({'name':name, 'genres':genres, 'city':city, 'state':state,'address':address, 'phone':phone, 'website':website, 'facebook_link':facebook_link, 'seeking_talent':seeking_talent, 'seeking_description': seeking_description, 'image_link': image_link})
    db.session.commit()
  except:
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    flash('The Venue was succesfully edited')
  if error:
    return render_template('pages/home.html')
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form['name']
    genres = ','.join(request.form.getlist('genres'))
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = True if request.form['seeking_venue'] else False
    seeking_description = request.form['seeking_venue']
    image_link = request.form['image_link']
    create_artist = Artist(name=name, genres=genres, city=city, state=state, phone=phone, website=website, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link)
    db.session.add(create_artist)
    db.session.commit()
  except: 
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  if not error:
    flash('Artist ' + name + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  body = {}
  error = False
  confirm = request.get_json()['confirm_id']
  try:
    if(confirm == artist_id):
      delete_artist = Artist.query.get(artist_id)
      db.session.delete(delete_artist)
      db.session.commit()
      body['result'] = 'deleted'
      flash('The artist was succesfully deleted!')
    else:
      body['result'] = 'not deleted'
      flash('The confirmation id is not correct, the artist has not been deleted')
  except: 
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return jsonify(body)
  if not error:
    return jsonify(body)
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.order_by('start_time').all()
  data = []
  for show in shows:
    the_show = {}
    the_show["venue_id"] = show.venue_id
    the_show["venue_name"] = Venue.query.filter_by(id=show.venue_id).first().name
    the_show["artist_id"] = show.artist_id
    the_show["artist_name"] = Artist.query.filter_by(id=show.artist_id).first().name
    the_show["artist_image_link"] = Artist.query.filter_by(id=show.artist_id).first().image_link
    the_show["start_time"] = show.start_time
    data.append(the_show)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    new_show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    db.session.close()
  except: 
    error = True
    flash('Oops, there was an error, please try again!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  if not error:
    flash('Show was successfully listed!')
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
