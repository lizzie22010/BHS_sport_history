from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html", title="Home")


if __name__ == '__main__':
    # TAKE OUT BEFORE SUBMIT
    app.run(debug=True)
