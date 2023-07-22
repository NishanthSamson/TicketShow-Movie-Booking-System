from flask import Flask, render_template, request, url_for, redirect, jsonify, abort, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user, UserMixin, RoleMixin, logout_user, LoginForm, login_user
from flask_security.utils import hash_password
from werkzeug.utils import secure_filename
from flask_bcrypt import *
from datetime import datetime
from flask import Flask
from celery import Celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'MAD2PROJECT'
app.config['UPLOAD_FOLDER'] = 'static\\uploads'
app.config['SECURITY_PASSWORD_SALT'] = 'SALT'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
db = SQLAlchemy(app)
  
class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("user.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String(300))
    phone = db.Column(db.Integer())
    gender = db.Column(db.String(10))
    address = db.Column(db.String(300))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        "Role", secondary="roles_users", backref=db.backref("users", lazy="dynamic")
    )

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    img = db.Column(db.String(300))
    genre = db.Column(db.String(50))
    rating = db.Column(db.Float)
    desc = db.Column(db.String(1000))

class Theatres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.String(200), nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'))
    theatre = db.relationship('Theatres', backref=db.backref('bookings'))
    nos = db.Column(db.Integer)
    cost = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('bookings'))
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id'))
    show = db.relationship('Shows', backref=db.backref('bookings'))

class Shows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tickets = db.Column(db.Integer, default=100)
    date = db.Column(db.Date())
    starttime = db.Column(db.DateTime())
    price = db.Column(db.Integer, default=100)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    movie = db.relationship('Movies', backref=db.backref('shows'))
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'))
    theatre = db.relationship('Theatres', backref=db.backref('shows'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


with app.app_context():
    db.create_all()
    a = user_datastore.find_user(email='admin@gmail.com')
    # b = Movies.query.get(1)
    c = Theatres.query.get(1)
    if not a:
        user_datastore.create_user(email='admin@gmail.com', password=hash_password('123'))
    # if(b == None):
    #     new_movie = Movies(name='oppenheimer')
    #     db.session.add(new_movie)
    #     db.session.commit()
    if(c == None):
        new_theatre = Theatres(name='INOX')
        db.session.add(new_theatre)
        db.session.commit()


@celery.task
def send_daily_reminder():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if(user.email!='admin@gmail.com'):
                email_address = user.email
                email_subject = 'Daily Reminder'
                email_body = 'This is a reminder to complete your tasks today!'
                send_email(email_address, email_subject, email_body)

@celery.task
def send_monthly_newsletter():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if(user.email!='admin@gmail.com'):
                email_address = user.email
                email_subject = 'Monthly Newsletter'
                email_body = generate_newsletter()
                send_news(email_address, email_subject, email_body)           

def generate_newsletter():
    with open('templates/newsletter.html', 'r') as file:
        template_content = file.read()
    movies = Movies.query.order_by(Movies.id.desc()).limit(5).all()
    rendered_template = render_template_string(template_content, movies=movies)

    return rendered_template

def send_email(to_address, subject, body):
    from_address = 'ticketshowv2@gmail.com'
    password = 'jjnsqsvuufljlfxs'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = to_address
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(from_address, password)
            smtp.send_message(message)
            print('Reminder email sent successfully.')
    except Exception as e:
        print('Failed to send reminder email:', str(e))

def send_news(to_address, subject, body):
    from_address = 'ticketshowv2@gmail.com'
    password = 'jjnsqsvuufljlfxs'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = to_address
    message['Subject'] = subject

    message.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(from_address, password)
            smtp.send_message(message)
            print('Reminder email sent successfully.')
    except Exception as e:
        print('Failed to send reminder email:', str(e))


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated and current_user.email == 'admin@gmail.com':
        return redirect(url_for('manage_theatres'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.email == 'admin@gmail.com':
        return redirect(url_for('admin'))
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    logout_user()

@app.route('/admin/manage/theatres', methods=['GET', 'POST'])
def manage_theatres():
    uname=current_user.email
    if not current_user.is_authenticated or current_user.email != 'admin@gmail.com':
        return abort(403)
    return render_template('managetheatres.html',uname=uname)

@app.route('/admin/manage/movies', methods=['GET', 'POST'])
def manage_movies():
    if not current_user.is_authenticated or current_user.email != 'admin@gmail.com':
        return abort(403)
    return render_template('managemovies.html')

@app.route('/admin/manage/<int:theatre_id>', methods=['GET', 'POST'])
def manage(theatre_id):
    if not current_user.is_authenticated or current_user.email != 'admin@gmail.com':
        return abort(403)
    return render_template('manage.html', theatre_id = theatre_id)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_datastore.create_user(
            email=request.form.get('email'),
            password=hash_password(request.form.get('password'))
        )
        db.session.commit()

        return redirect(url_for('account'))

    return render_template('register.html')


@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    return render_template('account.html', uname=current_user.username, uemail=current_user.email, uimg=current_user.img, uphone=current_user.phone, ugender=current_user.gender, uaddress=current_user.address)

# @app.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html')

@app.route('/movie/<int:movie_id>/view/', methods=('GET', 'POST'))
@login_required
def view_movie(movie_id):
    movie = Movies.query.get_or_404(movie_id)
    return render_template('movies.html', movie=movie)

@app.route('/movies', methods=('GET', 'POST'))
def movies():
    return render_template('allmovies.html')

@app.route('/booking', methods=['GET','POST'])
@login_required
def booking():
    return render_template('booking.html')

@app.route('/accprofilepic', methods=['GET','POST'])
def accprofilepic():
    return render_template('profilepic.html')


@app.route('/mybookings', methods = ['GET'])
@login_required
def mybookings():
    return render_template('mybookings.html')

@app.route('/search/results', methods=['GET'])
def search_results():
    # Retrieve the query string from the URL parameters
    query_string = request.args.get('query', '')
    
    # Query the database based on the query string
    movies = Movies.query.filter(Movies.name.ilike(f"%{query_string}%")).all()
    
    # Pass the search results data to the 'results.html' template
    return render_template('results.html', movies=movies)

@app.route('/edit_theatre/<int:theatre_id>', methods=['GET','POST'])
def edit_theatre(theatre_id):
    theatre = Theatres.query.get_or_404(theatre_id)
    return render_template('edittheatre.html', theatre=theatre)

@app.route('/edit_movie/<int:movie_id>', methods=['GET','POST'])
def edit_movie(movie_id):
    movie = Movies.query.get_or_404(movie_id)
    return render_template('editmovies.html', movie=movie)



# @app.route('/api/search_movies', methods=['POST'])
# def search_movies():
#     data = request.json
#     query = data.get('query')

#     movies = Movies.query.filter(Movies.name.ilike(f"%{query}%")).all()

#     movies_data = [{'id': movie.id, 'name': movie.name, 'img': movie.img} for movie in movies]

#     return jsonify(movies_data)


@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movies.query.all()
    movie_list = []
    for movie in movies:
        movie_data = {
            'id': movie.id,
            'name': movie.name,
            'img' : movie.img
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

# @app.route('/api/shows', methods=['GET'])
# def get_shows():
#     shows = Shows.query.all()
#     shows_list = []
#     for show in shows:
#         show_data = {
#             'id': show.id,
#             'movie': show.movie,
#             'starttime': show.starttime,
#             'tickets': show.tickets,
#         }
#         shows_list.append(show_data)
#     return jsonify(shows_list)

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

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    data = request.json

    uname = data.get('uName')
    uphone = data.get('uPhone') 
    ugender = data.get('uGender')
    uaddress = data.get('uAddress')

    user_id = current_user.id
    user = User.query.filter_by(id = user_id).first()

    user.username = uname
    user.phone=uphone
    user.gender=ugender
    user.address = uaddress

    db.session.commit()

    response = {
        'message': 'Details Updated successfully!'
    }

    return jsonify(response)

@app.route('/api/profilepic/', methods=('GET', 'POST'))
@login_required
def profilepic():
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    file = request.files['file']
    filename = secure_filename(file.filename)

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    user.img=filename
    db.session.commit()

    response = {
        'message': 'Profile Picture Updated successfully!'
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
        if(show.tickets>=num_tickets and num_tickets>0):    
            show_data = {
                'id': show.id,
                'starttime': show.starttime,
                'tickets': show.tickets,
                'theatreId': show.theatre_id,
                'theatreName': show.theatre.name
            }
            shows_list.append(show_data)
    return jsonify(shows_list)

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

@app.route('/api/edit_theatre', methods=['POST'])
def e_theatre():
    data = request.json

    theatre_id = data.get('theatreId')
    theatre_name = data.get('theatreName')


    theatre = Theatres.query.get_or_404(theatre_id)
    theatre.name = theatre_name

    db.session.commit()

    response = {
        'message': 'Theatre edited successfully!'
    }

    return jsonify(response)

@app.route('/api/remove_theatre', methods=['GET','POST'])
def remove_theatre():
    data = request.json
    theatre_id = data.get('theatreId')
    # Retrieve the theatre from the database
    theatre = Theatres.query.get_or_404(theatre_id)

    # Delete associated shows for the theatre
    shows = Shows.query.filter_by(theatre_id=theatre_id).all()
    for show in shows:
        # Delete associated bookings for each show
        bookings = Bookings.query.filter_by(show_id=show.id).all()
        for booking in bookings:
            db.session.delete(booking)

        db.session.delete(show)

    # Delete the theatre itself
    db.session.delete(theatre)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"Theatre with ID {theatre_id} and its associated shows and bookings have been removed successfully."})



# @app.route('/api/remove_theatre', methods=['POST'])
# def remove_theatre():
#     data = request.json

#     theatre_id = data.get('theatreId')

#     theatre = Theatres.query.filter_by(id=theatre_id).first()
#     db.session.delete(theatre)
#     db.session.commit()

#     response = {
#         'message': 'Theatre removed successfully!'
#     }

#     return jsonify(response)

@app.route('/api/add_movie', methods=['POST'])
def add_movie():
    data = request.form

    movie_name = data.get('movieName')
    movie_desc = data.get('movieDesc')
    file = request.files['file']
    filename = secure_filename(file.filename)

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_movie = Movies(name=movie_name, desc=movie_desc, img=filename)
    db.session.add(new_movie)
    db.session.commit()

    response = {
        'message': 'Movie added successfully!'
    }

    return jsonify(response)

@app.route('/api/edit_movie', methods=['POST'])
def e_movie():
    data = request.json

    movie_id = data.get('movieId')
    movie_name = data.get('movieName')
    movie_desc = data.get('movieDesc')

    movie = Movies.query.get_or_404(movie_id)
    movie.name = movie_name
    movie.desc = movie_desc

    db.session.commit()

    response = {
        'message': 'Movie edited successfully!'
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
    # Retrieve the show from the database
    show = Shows.query.get_or_404(show_id)

    # Delete associated bookings for the show
    bookings = Bookings.query.filter_by(show_id=show_id).all()
    for booking in bookings:
        db.session.delete(booking)

    # Delete the show itself
    db.session.delete(show)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"Show with ID {show_id} and its associated bookings have been removed successfully."})


@app.route('/api/my_bookings', methods = ['GET'])
def my_bookings():
    user_id = current_user.id
    bookings = Bookings.query.filter_by(user_id = user_id).all()
    booking_list = []
    for booking in bookings:
        bk_data = {
            'movie': booking.show.movie.name,
            'theatre': booking.theatre.name,
            'tickets': booking.nos,
            'starttime': booking.show.starttime,
            'img': booking.show.movie.img
        }
        booking_list.append(bk_data)
    return jsonify(booking_list)

@app.route('/send_reminder')
def send_reminder():
    send_daily_reminder.delay()
    return 'Reminder task sent!'

@app.route('/send_newsletter')
def send_newsletter():
    send_monthly_newsletter.delay()
    return 'Newsletter sent!'

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