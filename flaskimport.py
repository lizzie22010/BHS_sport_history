from flask import Flask, render_template, g, abort
import sqlite3

app = Flask(__name__)


# Function to get the database connection
# Creates the database and tables if they don't exist


def get_db():
    # store the database connection
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('BHS_sport_history_database.db')
        db.row_factory = sqlite3.Row
        # Create tables if they don't exist
        c = db.cursor()
        # Athlete table for storing athlete details
        c.execute('''CREATE TABLE IF NOT EXISTS athlete (
                        athlete_id INTEGER PRIMARY KEY
                                        NOT NULL,
                        firstname  TEXT    NOT NULL,
                        lastname   TEXT    NOT NULL,
                        formclass  TEXT
                    )''')
        db.commit()
    return db


# Automatically close the database connection after each request
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def home():
    return render_template("home.html", title="Home")


@app.route('/athletes')
def athletes():
    return render_template('athletes.html')


@app.route("/all_athletes")
def all_athletes():
    db = get_db()
    cursor = db.execute('SELECT * FROM athlete')
    athletes = cursor.fetchall()
    db.close()
    return render_template('all_athletes.html', title='ALL ATHLETES',
                           athletes=athletes)


@app.route("/award")
def award():
    return render_template('award.html')


# getting the player info from database
def get_player(athlete_id):
    db = get_db()
    cursor = db.execute('''
    SELECT *
    FROM athlete
    WHERE athlete_id = ?
    ''', (athlete_id,))
    athlete = cursor.fetchone()
    db.close()
    return athlete


# getting info to be displayed on player profiles
@app.route("/player/<int:athlete_id>")
def player_profile(athlete_id):
    db = get_db()
# join athlete to sport to get sport_name for each athlete
    cursor_sport_name = db.execute('''
        SELECT athlete.athlete_id, sport.sport_name
        FROM athlete
        JOIN athlete_sport ON athlete.athlete_id = athlete_sport.athlete_id
        JOIN sport ON athlete_sport.sport_id = sport.sport_id
        WHERE athlete.athlete_id = ?
        ''', (athlete_id,))
    rows = cursor_sport_name.fetchall()
# join athlete to award to get award_name for each athlete
    cursor_award_name = db.execute('''
        SELECT athlete.athlete_id, award.award_name
        FROM athlete
        JOIN athlete_award ON athlete.athlete_id = athlete_award.athlete_id
        JOIN award ON athlete_award.award_id = award.award_id
        WHERE athlete.athlete_id = ?
        ''', (athlete_id,))
    awards = cursor_award_name.fetchall()
    athlete = get_player(athlete_id)
# if no athlete with that id exists, show 404
    if not athlete:
        abort(404)
# separate so that rest of player profile page works when there is no award
    if not awards:
        awards = [""]
    return render_template("player.html", athlete=athlete, rows=rows, awards=awards)


@app.route("/award/<int:award_id>")
def award_page(award_id):
    db = get_db()
    cursor = db.execute('''
        SELECT award_name, description
        FROM award
        WHERE award_id = ?''',
        (award_id,))
    award_info = cursor.fetchone()
    return render_template("award_page.html", award_info=award_info )

# error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    # TAKE OUT BEFORE SUBMIT
    app.run(debug=True)
