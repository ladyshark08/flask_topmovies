from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

API_KEY = "edfaa1fe154f60eaf7a2e37215895717"

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


@app.route("/")
def home():
    result = db.session.execute(db.select(Movies).order_by(Movies.ranking))
    all_movies = result.scalars()
    # second_session = db.session.execute(db.select(Book).order_by(Book.title))
    # second_all_bs = second_session.scalars()

    return render_template("index.html", movies=all_movies)


@app.route("/edit/<int:movie_id>", methods=['POST', 'GET'])
def update(movie_id):
    form = UpdateForm()
    if request.method == "POST" and form.validate_on_submit():
        new_rating = request.form.get("new_rating")
        new_review = request.form.get("your_review")
        movie_to_update = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
        movie_to_update.rating = new_rating
        movie_to_update.review = new_review
        db.session.commit()
        return redirect('/')

    movie = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
    return render_template("edit.html", movie=movie, form=form)


@app.route('/delete/<int:movie_id>', methods=["POST", "GET"])
def delete_movie(movie_id):
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

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9"
                             ".eyJhdWQiOiJlZGZhYTFmZTE1NGY2MGVhZjdhMmUzNzIxNTg5NTcxNyIsInN1YiI6IjY1YzZhNWI0YjZjZmYxMDE2NGE0MmEyNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.l6aTkcWI81-J81naWrXdYWAVR-FYnnonicTAsW6rXXg"
        }

        response = requests.get(url, headers=headers)
        result = response.json()
        print(result["results"])

    return render_template('add.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
