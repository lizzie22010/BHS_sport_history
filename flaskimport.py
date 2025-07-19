from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html", title="Home")


@app.route('/athletes')
def athletes():
    return render_template('athletes.html')


@app.route("/award")
def award():
    return render_template('award.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    # TAKE OUT BEFORE SUBMIT
    app.run(debug=True)
