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


if __name__ == '__main__':
    # TAKE OUT BEFORE SUBMIT
    app.run(debug=True)
