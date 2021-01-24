from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'

Bootstrap(app)
db = SQLAlchemy()
db.init_app(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)


#with app.app_context():
    #db.create_all()

class RealMovieForm(FlaskForm):
    rating = StringField('Your rating out of 10', [DataRequired()])
    review = StringField("Your review",[DataRequired()])
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title", [DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    movies = db.session.query(Movie).all()
    return render_template("index.html", movies=movies)


@app.route("/edit/<movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    movie = Movie.query.get(movie_id)
    form = RealMovieForm(obj=movie)
    if form.validate_on_submit():
        form.populate_obj(movie)
        movie.save()

    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete/<movie_id>")
def delete(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        title = request.form['title']
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": API_KEY,
            "language": "en-US",
            "query": title,
        }
        data = requests.get(url, params)
        response = data.json()
        movies = response['results']
        return render_template("select.html", movies=movies)
    
    return render_template("add.html", form=form)


@app.route('/selection/<movie_id>', methods=['POST', 'GET'])
def selection(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
    }
    data = requests.get(url, params)
    response = data.json()
    movie = Movie()
    movie.title = response['title']
    movie.img_url = f"https://image.tmdb.org/t/p/w500{response['backdrop_path']}"
    movie.year = response['release_date']
    movie.description = response['overview']
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
