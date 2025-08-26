from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)


# Function to get the database connection
# Creates the database and tables if they don't exist


def get_db():
    # Use Flask's application context to store the database connection
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('BHS_sport_history_database.db')
        db.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
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


# Close the database connection after each request
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
    return render_template('all_athletes.html', title='ALL ATHLETES', athletes=athletes)


@app.route("/award")
def award():
    return render_template('award.html')


# athlete pages
@app.route("/athlete/1")
def athlete1():
    return render_template('athlete/1.html')


# getting the player info from database
def get_player(player_id):
    db = get_db()
    cursor = db.execute("SELECT * FROM athlete WHERE athlete_id = ?", (player_id,))
    player = cursor.fetchall()
    db.close()
    return player


@app.route("/player/<int:player_id>")
def player_profile(player_id):
    athlete = get_player(player_id)
    if not athlete:
        page_not_found(404)  # fix here see if works
    return render_template("player.html", athlete=athlete)


#error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    # TAKE OUT BEFORE SUBMIT
    app.run(debug=True)
