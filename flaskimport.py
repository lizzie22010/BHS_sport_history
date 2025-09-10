from flask import Flask, render_template, g, abort, request
import sqlite3

app = Flask(__name__)


def get_db():
    # stores the database connection for db = get_db() 
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('BHS_sport_history_database.db')
        db.row_factory = sqlite3.Row
    return db


# automatically close the database connection after each request
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# page for each article using article.html
@app.route("/article/<int:article_id>")
def article_page(article_id):
    db = get_db()
# get all info from article table
    cursor = db.execute("""
        SELECT *
        FROM article
        WHERE article_id = ?
    """, (article_id,))
    article = cursor.fetchone()
    return render_template("article.html", article=article)


# getting the articles for display on the homepage
def get_all_articles():
    db = get_db()
    cursor = db.execute("""
        SELECT *
        FROM article
        ORDER BY article_id ASC
    """)
    articles = cursor.fetchall()
    return articles


# selecting 4 random athletes and their sport from the database for the homepage
def select_random_athlete():
    db = get_db()
    cursor = db.execute("""
        SELECT athlete.athlete_id, athlete.firstname, athlete.lastname, sport.sport_name
        FROM athlete
        JOIN athlete_sport ON athlete.athlete_id = athlete_sport.athlete_id
        JOIN sport ON athlete_sport.sport_id = sport.sport_id
        ORDER BY RANDOM()
        LIMIT 4
    """)
    athletes = cursor.fetchall()
    return athletes


# homepage
@app.route('/')
# get the athlete's articles for hompage display
def show_articles():
    articles = get_all_articles()
    athletes = select_random_athlete()
    return render_template("home.html", articles=articles, title="Home", athletes=athletes)


# def to be used in app route /athletes and /all_athletes
def fetch_all_athletes():
    db = get_db()
# get all athletes for the all_athletes list 
    cursor = db.execute('SELECT * FROM athlete')
    athletes = cursor.fetchall()
    return athletes


@app.route('/athletes')
def athletes():
    athletes = fetch_all_athletes()
    return render_template('athletes.html', athletes=athletes)


@app.route("/all_athletes")
def get_all_athletes():
    athletes = fetch_all_athletes()
    return render_template('all_athletes.html', athletes=athletes)


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
        SELECT athlete.athlete_id, award.award_name, award.award_id
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
        SELECT award_name, trophy_name, description, award_id
        FROM award
        WHERE award_id = ?''',
        (award_id,))
    award_info = cursor.fetchone()
# if there is no award of that id then abort(404)
    if not award_info:
        abort(404)
    return render_template("award_page.html", award_info=award_info)


@app.route("/add_athlete", methods=['GET', 'POST'])
def add_athlete_page():
    db = get_db()
    cursor = db.cursor()
    # gets options for sport dropdown
    cursor.execute('''
        SELECT sport_name
        FROM sport
        ORDER BY sport_name
        ''')
    sports = cursor.fetchall()
    # gets options for the awards dropdown
    cursor.execute('''
        SELECT award_name 
        FROM award
        ORDER BY award_name''')
    awards = cursor.fetchall()

    # message is so that if something goes wrong it will tell the user
    message = ""
    if request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        lastname = request.form.get('lastname', '').strip()
        sport_name = request.form.get('sport')
        award_name = request.form.get('award')
        award_year = request.form.get('award_year')
        try:
            award_year = int(award_year)
            add_athlete(firstname, lastname, sport_name, award_name, award_year)
            message = f"Athlete '{firstname} {lastname}' added successfully."
        except Exception as e:
            message = f"Error: {str(e)}"
    return render_template( 'add_athlete.html', sports=sports, awards=awards, message=message)


# def for form to insert athletes and their awards into the database
def add_athlete(firstname, lastname, sport_name, award_name, award_year):
    db = get_db()
    cursor = db.cursor()
# insert athlete into athlete table if they don't already exist
    cursor.execute('''
        INSERT INTO athlete (firstname, lastname)
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1
            FROM athlete
            WHERE firstname = ? AND lastname = ?
        )
        ''', (firstname, lastname, firstname, lastname))
# get the athlete_id of the inserted athlete
    cursor.execute('''
        SELECT athlete_id
        FROM athlete
        WHERE firstname = ? AND lastname = ?
        ''', (firstname, lastname))
    athlete_id = cursor.fetchone()['athlete_id']
# get sport_id for the sport the athlete plays
    cursor.execute('''
        SELECT sport_id
        FROM sport
        WHERE sport_name = ?
        ''', (sport_name,))
    sport = cursor.fetchone()
    if not sport:
        raise ValueError(f"Sport '{sport_name}' not found in database.")
    sport_id = sport['sport_id']
# insert athlete_sport if it does not exist
    cursor.execute('''
        INSERT INTO athlete_sport (athlete_id, sport_id)
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1
            FROM athlete_sport
            WHERE athlete_id = ? AND sport_id = ? 
        )
    ''', (athlete_id, sport_id, athlete_id, sport_id))
# get award_id of the award
    cursor.execute('''SELECT award_id
        FROM award
        WHERE award_name = ?
        ''', (award_name,))
    award = cursor.fetchone()
    if not award:
        raise ValueError(f"Award '{award_name}' not found in database.")
    award_id = award['award_id']
# insert athlete_award if not exists
    cursor.execute('''
        INSERT INTO athlete_award (athlete_id, award_id, award_year)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 
            FROM athlete_award
            WHERE athlete_id = ? AND award_id = ? AND award_year = ?
        )
    ''', (athlete_id, award_id, award_year, athlete_id, award_id, award_year))
    db.commit()
    print("Adding athlete:", firstname, lastname)

# error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    # TAKE OUT BEFORE SUBMIT
    app.run(debug=True)
