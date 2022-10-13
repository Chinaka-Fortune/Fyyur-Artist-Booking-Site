#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
 
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# For Venues table
class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy=True)
    
    def __repr__(self):
           return f'<Venue ID: {self.id}, name: {self.name}>'
         
  
    # Artists table

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    looking_for_venues = db.Column(db.Boolean, nullable=False, default=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


# For shows table
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time =db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, datetime):
    value = value.strftime('%Y-%m-%d %H:%M:%S')
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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  return render_template('pages/venues.html', venues=Venue.query.all());

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Implimenting Venues search
  search_term = request.form.get('search_term', '')
  if search_term:
      search_result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
      response = {
        'count': len(search_result),
        'data': search_result
      }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))    
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Inplimenting show_venue using venue_id
  past_shows = []
  upcoming_shows = []
  current_date = datetime.now()
  venue = Venue.query.get(venue_id)
  for show in venue.shows:
    if show.start_time > current_date:
        upcoming_shows.append(show)
    else:
      past_shows.append(show)
  data = vars(venue)
  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = 'past_shows_count'

  data = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
# Creates new shows
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    if request.method == 'POST':
        venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          image_link=form.image_link.data,
          website=form.website_link.data,
          seeking_talent=form.seeking_talent.data,
          seeking_description=form.seeking_description.data
        )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('You just got an error. Venue ' + request.form['name'] + ' was not listed successfully.')
  finally:
    db.session.close()
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # To delete venues
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted.')
  except:
    db.session.rollback()
    flash('An error occured. Venue could not be deleted.')
  finally:
    db.session.close
    return jsonify({'success': True})
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search for artists
  
  search_term = request.form.get('search_term', '')
  if search_term != '':
    search_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    response = {
      'count': len(search_results),
      'data': search_results
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  
  past_shows = []
  current_date = datetime.now()
  upcoming_shows = []
  artist = Artist.query.get(artist_id)
  for show in artist.shows:
    if show.start_time > current_date:
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
      
  data = vars(artist)
  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)
  
  
  data = Artist.query.get(artist_id)
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(obj=artist)
  artist = Artist.query.get(artist_id)
  print(form.data)
   
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Takes values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website = form.website_link.data,
      looking_for_venues = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was updated successfully!')
    except:
      db.session.rollback()
      flash('An error occured. Artist, ' + request.form['name'] + ' could not be updated.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message))
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  print(form.data)
  
  # TODO: populate form with values from venue with ID <venue_id>
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('You just got an error. Venue ' + request.form['name'] + ' was not listed successfully.')
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message))
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  if form.validate_on_submit():
    try:
      artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website = form.website_link.data,
      looking_for_venues = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('You just got an error. Artist, ' + request.form['name'] + ' was not listed successfully.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message))
      
  return render_template('pages/home.html')
  
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  data = []
  shows = Show.query.all()
  for show in shows:
    if show.start_time > datetime.now():
      data.append({
        'venue_id': show.venue_id,
        'venue_name': show.Venue.name,
        'artist_id': show.artist_id,
        'artist_name': show.Artist.name,
        'artist_image_link': show.Artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
    if request.method == 'POST':
        show = Show(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data,
          start_time = form.start_time.data
        )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  
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
