from flask import Flask, render_template, request, url_for, redirect, session, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.utils import secure_filename
from flask_bcrypt import *
from datetime import datetime
# from sqlalchemy.sql import func
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'MAD2PROJECT'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
  

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    img = db.Column(db.String(300))

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    img = db.Column(db.String(300))

class Theatres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.String(200), nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'))
    theatre = db.relationship('Theatres', backref=db.backref('bookings'))
    nos = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('bookings'))
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id'))
    show = db.relationship('Shows', backref=db.backref('bookings'))

class Shows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tickets = db.Column(db.Integer, default=100)
    date = db.Column(db.Date())
    starttime = db.Column(db.DateTime())
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    movie = db.relationship('Movies', backref=db.backref('shows'))
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'))
    theatre = db.relationship('Theatres', backref=db.backref('shows'))

    
    

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')      

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class PostForm(FlaskForm):
    number = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Number of tickets"})
    
    submit = SubmitField('Post')

@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()
        a = User.query.filter_by(username='admin').first()
        b = Movies.query.get(1)
        c = Theatres.query.get(1)
    if(not a):
        hashed_password = generate_password_hash('123')
        new_user = User(username='admin', password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
    if(b == None):
        new_movie = Movies(name='oppenheimer')
        db.session.add(new_movie)
        db.session.commit()

       
    if(c == None):
        new_theatre = Theatres(name='INOX')
        db.session.add(new_theatre)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_required
def admin():
    uname = current_user.username
    return render_template('dashboard.html',uname=uname)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global uname
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                name = form.username.data
                session['username'] = name
                uname = session.get('username')
                return redirect(url_for('account'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', uname=uname)


@app.route('/booking', methods=['GET','POST'])
def booking():
    return render_template('booking.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movies.query.all()
    movie_list = []
    for movie in movies:
        movie_data = {
            'id': movie.id,
            'name': movie.name,
        }
        movie_list.append(movie_data)
    return jsonify(movie_list)

@app.route('/api/theaters', methods=['GET'])
def get_theatres():
    theatres = Theatres.query.all()
    theatre_list = []
    for theatre in theatres:
        theatre_data = {
            'id': theatre.id,
            'name': theatre.name,
            'shows': serialize_shows(theatre.shows)
        }
        theatre_list.append(theatre_data)
    return jsonify(theatre_list)

@app.route('/api/shows', methods=['GET'])
def get_shows():
    shows = Shows.query.all()
    shows_list = []
    for show in shows:
        show_data = {
            'id': show.id,
            'movie': show.movie,
            'starttime': show.starttime,
            'tickets': show.tickets,
        }
        shows_list.append(show_data)
    return jsonify(shows_list)

@app.route('/api/book_tickets', methods=['POST'])
def book_tickets():
    data = request.json

    show_id = data.get('showId')
    movie_id = data.get('movieId')
    theater_id = data.get('theatreId') 
    num_tickets = data.get('numTickets')

    userid = current_user.id

    new_booking = Bookings(user_id = userid, show_id = show_id, movie=movie_id, theatre_id=theater_id, nos = num_tickets)
    db.session.add(new_booking)
    show = Shows.query.filter_by(id=show_id).first()
    show.tickets -= num_tickets
    db.session.add(show)
    db.session.commit()

    response = {
        'message': 'Tickets booked successfully!'
    }

    return jsonify(response)

@app.route('/api/allshows', methods=['POST'])
def all_shows():
    data = request.json

    movie_id = data.get('movieId')
    date = data.get('date')
    num_tickets = data.get('numTickets')

    shows = Shows.query.filter_by(movie_id=movie_id, date=date).all()
    shows_list = []
    for show in shows:
        if(show.tickets>=num_tickets):    
            show_data = {
                'id': show.id,
                'starttime': show.starttime,
                'tickets': show.tickets,
                'theatreId': show.theatre_id,
                'theatreName': show.theatre.name
            }
            shows_list.append(show_data)
    return jsonify(shows_list)


# @app.route('/profile')
# @login_required
# def profile():
#     username = current_user.username
#     return f'Welcome, {username}!'

@app.route('/api/add_theatre', methods=['POST'])
def add_theatre():
    data = request.json

    theatre_name = data.get('theatreName')

    new_theatre = Theatres(name=theatre_name)
    db.session.add(new_theatre)
    db.session.commit()

    response = {
        'message': 'Theatre added successfully!'
    }

    return jsonify(response)

@app.route('/api/remove_theatre', methods=['POST'])
def remove_theatre():
    data = request.json

    theatre_id = data.get('theatreId')

    theatre = Theatres.query.get_or_404(theatre_id)
    db.session.delete(theatre)
    db.session.commit()

    response = {
        'message': 'Theatre removed successfully!'
    }

    return jsonify(response)

@app.route('/api/add_movie', methods=['POST'])
def add_movie():
    data = request.json

    movie_name = data.get('movieName')

    new_movie = Movies(name=movie_name)
    db.session.add(new_movie)
    db.session.commit()

    response = {
        'message': 'Movie added successfully!'
    }

    return jsonify(response)

@app.route('/api/add_show', methods=['POST'])
def add_show():
    data = request.json

    stime = data.get('startTime')
    show_tickets = data.get('tickets')
    show_movie = data.get('showMovieId')
    show_theatre = data.get('theatreId')

    show_time = datetime.strptime(stime, "%Y-%m-%dT%H:%M")
    show_date = show_time.date()

    new_show = Shows(tickets=show_tickets, starttime = show_time, date = show_date, movie_id = show_movie, theatre_id = show_theatre)
    db.session.add(new_show)
    db.session.commit()

    response = {
        'message': 'Show added successfully!'
    }

    return jsonify(response)

@app.route('/api/remove_show', methods=['POST'])
def remove_show():
    data = request.json

    show_id = data.get('showId')

    show = Shows.query.get_or_404(show_id)
    db.session.delete(show)
    db.session.commit()

    response = {
        'message': 'Show removed successfully!'
    }

    return jsonify(response)

def serialize_shows(shows):
    serialized_shows = []
    for show in shows:
        serialized_show = {
            'id': show.id,
            'tickets': show.tickets,
            'starttime': show.starttime.isoformat(),
            'movie': serialize_movie(show.movie),
            'theatre': show.theatre.name
        }
        serialized_shows.append(serialized_show)
    return serialized_shows

def serialize_movie(movie):
    return {
        'id': movie.id,
        'name': movie.name
    }

if __name__ == '__main__':
    app.run(debug=True)