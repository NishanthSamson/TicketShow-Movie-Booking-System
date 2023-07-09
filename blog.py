from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.utils import secure_filename
from flask_bcrypt import *
import os
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static\\uploads'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)      
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False)
    img = db.Column(db.String(300))
    bio = db.Column(db.String(500), default="Author Description")

class Post(db.Model, UserMixin):
    pno = db.Column(db.Integer, primary_key=True)      
    title = db.Column(db.String(100), nullable=False)
    blogbody = db.Column(db.String(20000), nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    author = db.Column(db.String(30), nullable=False)
    img = db.Column(db.String(300))
    likes = db.Column(db.Integer, default=0)      
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts'))

class Comment(db.Model, UserMixin):
    cid = db.Column(db.Integer, primary_key=True)
    pno = db.Column(db.Integer)   
    cmt = db.Column(db.String(20000), nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    author = db.Column(db.String(30), nullable=False)
    img = db.Column(db.String(300))
    

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
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Title"})

    blogbody = StringField(validators=[
                             InputRequired(), Length(min=8, max=2000)], render_kw={"placeholder": "Blog body"})
    
    bio = StringField(validators=[
                             InputRequired(), Length(min=8, max=2000)], render_kw={"placeholder": "Blog body"})

    submit = SubmitField('Post')

@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    tposts = Post.query.order_by(Post.likes.desc()).limit(4)  
    posts = Post.query.order_by(Post.time_created.desc()).all()
    return render_template('index.html',posts=posts, tposts = tposts)


@app.route('/post')
@login_required
def post():
    return render_template('post.html')

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

@app.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    posts = Post.query.order_by(Post.time_created.desc()).all()
    return render_template('blog.html', posts=posts, uname=uname)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html',uname=uname)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

@ app.route('/base', methods=['GET', 'POST'])
@login_required
def base():
    form = PostForm()
    user = User.query.filter_by(username=uname).first()
    if form.is_submitted():
        file = request.files['banner_image']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_post = Post(title=form.title.data, blogbody=form.blogbody.data,author = uname,img=filename, user_id = user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog'))

    return render_template('base.html', form=form)

@ app.route('/author', methods=['GET', 'POST'])
@login_required
def author():
    usr = request.args.get('usr', default=uname, type=str)
    user = User.query.filter_by(username=usr).all()
    posts = Post.query.filter_by(author=usr).all()
    return render_template('author.html', posts=posts, uname=usr, user = user)

@ app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = User.query.filter_by(username=uname).all()
    posts = Post.query.filter_by(author=uname).all()
    return render_template('account.html', posts=posts, uname=uname, user = user)

@app.route('/<int:post_id>/edit/', methods=('GET', 'POST'))
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()

    if form.is_submitted():
        post.title=form.title.data 
        post.blogbody=form.blogbody.data
        post.author = uname
        post.time_created = func.now()

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('blog'))

    return render_template('edit.html', form=form, post=post)

@app.route('/<int:post_id>/delete/')
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog'))

@app.route('/<int:post_id>/view/', methods=('GET', 'POST'))
@login_required
def view(post_id):
    post = Post.query.get_or_404(post_id)
    rposts = Post.query.order_by(Post.time_created).limit(3).all()
    user = User.query.filter_by(username=post.author).first()
    cc = Comment.query.filter_by(pno=post_id).count()
    
    like = request.args.get('like', default=0, type=int)
    if like == 1:
        post.likes -= 1
        db.session.commit()

    return render_template('post.html', post=post, uname=uname, rposts=rposts, like=like, user=user, cc=cc)


@app.route('/<int:post_id>/comments/', methods=('GET', 'POST'))
@login_required
def comments(post_id):
    user = User.query.filter_by(username=uname).first()
    filename = user.img
    if request.method == 'POST':
        textarea_input = request.form.get('comment')
        new_cmt = Comment(pno=post_id, cmt=textarea_input,author = uname, img=filename)
        db.session.add(new_cmt)
        db.session.commit()
    comments = Comment.query.filter_by(pno=post_id).order_by(Comment.time_created.desc()).all()
    return render_template('comments.html', comments=comments, uname=uname, user = user)


@app.route('/<string:uname>/profilepic/', methods=('GET', 'POST'))
@login_required
def profilepic(uname):
    user = User.query.filter_by(username=uname).first()
    form = PostForm()
    if form.is_submitted():
        file = request.files['profile_image']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.img = filename
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('account'))

    return render_template('profilepic.html', form=form)    

@app.route('/<int:post_id>/likes/', methods=('GET', 'POST'))
@login_required
def likes(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.filter_by(username=post.author).first()
    rposts = Post.query.order_by(Post.time_created).limit(3).all()
    cc = Comment.query.filter_by(pno=post_id).count()
    post.likes += 1
    db.session.add(post)
    db.session.commit()
    return render_template('likes.html',post=post,rposts=rposts,user=user, cc=cc)

@app.route('/<string:uname>/editbio/', methods=('GET', 'POST'))
@login_required
def editbio(uname):
    user = User.query.filter_by(username=uname).first()
    form = PostForm()

    if form.is_submitted():
        user.bio=form.bio.data 

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('account'))

    return render_template('editbio.html', form=form, user=user)



if __name__ == '__main__':
    app.run(debug = True)