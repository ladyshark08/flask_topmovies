from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import os

API_KEY = "edfaa1fe154f60eaf7a2e37215895717"

headers = {
    "accept": "application/json",
    "Authorization": os.environ.get("TOKEN")
}

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

# CREATE DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-collection.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6honzWlSihBXox7C0sKR6b'
db.init_app(app)

bootstrap = Bootstrap5(app)


# CREATE TABLE
class Movies(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class UpdateForm(FlaskForm):
    new_rating = FloatField('Your rating, out of 10 e.g 7.5', validators=[DataRequired()])
    your_review = StringField('Your Review', validators=[DataRequired()])
    done = SubmitField('Done')


class AddMovie(FlaskForm):
    movie_title = StringField('Movie Title', validators=[DataRequired()])
    add_movie = SubmitField('Add Movie')


def update_ranking():
    result = db.session.execute(db.select(Movies).order_by(Movies.rating))
    all_movies = result.scalars()
    rows = db.session.query(Movies).count()
    for movie in all_movies:
        movie.ranking = rows
        rows -= 1
    db.session.commit()


@app.route("/")
def home():
    with app.app_context():
        update_ranking()
        result = db.session.execute(db.select(Movies).order_by(Movies.rating))
        all_movies = result.scalars()
        second_session = db.session.execute(db.select(Movies).order_by(Movies.rating))
        second_all_bs = second_session.scalars()
        return render_template("index.html", movies=all_movies, movies_2=second_all_bs)


@app.route("/edit", methods=['POST', 'GET'])
def update():
    form = UpdateForm()
    code = request.args.get('code')
    if request.method == "POST" and form.validate_on_submit():
        new_rating = request.form.get("new_rating")
        new_review = request.form.get("your_review")
        movie_to_update = db.session.execute(db.select(Movies).where(Movies.id == code)).scalar()
        movie_to_update.rating = new_rating
        movie_to_update.review = new_review
        db.session.commit()
        return redirect('/')

    movie = db.session.execute(db.select(Movies).where(Movies.id == code)).scalar()
    return render_template("edit.html", movie=movie, form=form)


@app.route('/delete', methods=["POST", "GET"])
def delete_movie():
    movie_id = request.args.get('movie_id')
    movie_to_delete = db.get_or_404(Movies, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect("/")


@app.route('/add', methods=['POST', 'GET'])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():
        name = request.form.get('movie_title')
        url = f"https://api.themoviedb.org/3/search/movie?query={name}&include_adult=false&language=en-US&page=1"

        response = requests.get(url, headers=headers)
        result = response.json()
        result_processed = (result["results"])
        return render_template('select.html', movies=result_processed)

    return render_template('add.html', form=form)


@app.route("/select/<int:movie_id>")
def select_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    response = requests.get(url, headers=headers)
    result = response.json()
    url = result['poster_path']
    release_date = result['release_date'].split("-")
    year = release_date[0]
    title = result['original_title']
    new_movie = Movies(
        title=result['original_title'],
        img_url=f'https://image.tmdb.org/t/p/w500{url}',
        year=year,
        description=result['overview'],
        rating=0,
        ranking=0,
        review="not reviewed yet"
    )
    db.session.add(new_movie)
    db.session.commit()
    movie = db.session.execute(db.select(Movies).where(Movies.title == title)).scalar()
    tid = movie.id
    return redirect(url_for('update', code=tid))


if __name__ == '__main__':
    app.run(debug=True)
