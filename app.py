"""
EnviroAir — Flask web app for air-quality prediction, CSV preview, and MySQL auth.

Folder layout (standard Flask):
  app.py              — this file (entry point)
  requirements.txt    — Python dependencies
  templates/          — Jinja2 HTML pages
  static/             — JS/CSS assets (styling is mostly Tailwind CDN in templates)
  static/js/script.js — small client script for the preview page
  models/             — optional: place airs.pkl here (or keep in project root)
"""

from functools import wraps
from pathlib import Path
import pickle

from flask import Flask, redirect, render_template, request, session, url_for
import numpy as np
import pandas as pd

# MySQL is optional at import time; signup/login fail gracefully if not installed.
try:
    from flask_mysqldb import MySQL, MySQLdb
except ImportError:
    MySQL = None
    MySQLdb = None

# Project root = directory containing this file.
BASE_DIR = Path(__file__).resolve().parent

# Flask expects HTML under templates/ and public assets under static/.
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static",
)

# Required for Flask sessions (login state). Change this in production.
app.secret_key = "air_quality"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# --- MySQL (optional) ---
mysql = None
if MySQL is not None:
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = "root"
    app.config["MYSQL_DB"] = "air_quality"
    mysql = MySQL(app)

# --- ML model: prefer models/airs.pkl, fall back to project root airs.pkl ---
airs = None
model_load_error = None
_model_in_models = BASE_DIR / "models" / "airs.pkl"
_model_in_root = BASE_DIR / "airs.pkl"
model_path = _model_in_models if _model_in_models.exists() else _model_in_root

if model_path.exists():
    try:
        with open(model_path, "rb") as model_file:
            airs = pickle.load(model_file)
    except Exception as exc:
        model_load_error = str(exc)


def login_required(view):
    """Decorator: only allow the route if session contains a logged-in username."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# ----- Public routes (no login) -----


@app.route("/login")
def login():
    """Login form; redirects to home if already signed in."""
    if session.get("user"):
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/signup")
def signup():
    """Registration form; redirects to home if already signed in."""
    if session.get("user"):
        return redirect(url_for("home"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Clear session and return to login."""
    session.clear()
    return redirect(url_for("login"))


# ----- Protected routes (require session["user"]) -----


@app.route("/")
@login_required
def home():
    """Landing page after login."""
    return render_template("home.html")


@app.route("/home")
@login_required
def homee():
    """Alias route for the same home template."""
    return render_template("home.html")


@app.route("/viewdata")
@login_required
def upload():
    """CSV upload form (posts to getdata)."""
    return render_template("upload.html")


@app.route("/prediction")
@login_required
def prediction():
    """Form for pollutant inputs; prediction_text is None until POST /predict."""
    return render_template("prediction.html", prediction_text=None)


@app.route("/performance")
@login_required
def preformance():
    """Static demo metrics page (route name kept for backward compatibility)."""
    return render_template("performance.html")


@app.route("/chart")
@login_required
def chart():
    """Google Charts pie chart page."""
    return render_template("chart.html")


@app.route("/gallery")
@login_required
def gallery():
    """Image carousel page."""
    return render_template("gallery.html")


@app.route("/preview")
@login_required
def preview():
    """Empty preview until a file is uploaded via POST /getdata."""
    return render_template("preview.html", data=None)


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    """Run the pickled model on six numeric fields from the form."""
    if airs is None:
        if model_load_error:
            return render_template(
                "prediction.html",
                prediction_text=(
                    "Model load failed due to version mismatch. "
                    "Install compatible scikit-learn/numpy/scipy versions."
                ),
            )
        return render_template(
            "prediction.html",
            prediction_text="Model file not found. Add airs.pkl in models/ or project root.",
        )

    int_feature = [x for x in request.form.values()]
    final_features = [np.array(int_feature, dtype=float)]
    result = airs.predict(final_features)
    prediction_value = str(result[0]) if len(result) else "No result"
    return render_template("prediction.html", prediction_text=prediction_value)


@app.route("/getdata", methods=["POST"])
@login_required
def getdata():
    """Read uploaded CSV and render preview.html with a pandas DataFrame."""
    data = request.files["data"]
    data_csv = pd.read_csv(data)
    print(data_csv)
    return render_template("preview.html", data=data_csv)


# ----- Auth actions (public POST) -----


@app.route("/insertvalues", methods=["POST"])
def insertvalues():
    """Insert a new row into MySQL signup table; then redirect to login."""
    if mysql is None or MySQLdb is None:
        return render_template("signup.html", msg="MySQL dependency not installed.")

    cursors = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    cursors.execute("insert into signup values(%s,%s,%s)", (username, email, password))
    mysql.connection.commit()
    return redirect(url_for("login"))


@app.route("/log", methods=["POST"])
def log():
    """Validate username/password against MySQL; set session and redirect to home."""
    if mysql is None or MySQLdb is None:
        return render_template("login.html", msg="MySQL dependency not installed.")

    cursors = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    username = request.form["username"]
    password = request.form["password"]
    cursors.execute(
        "select * from signup where username=%s and password=%s",
        (username, password),
    )
    if cursors.fetchone():
        session["user"] = username
        return redirect(url_for("home"))
    return render_template("login.html", msg="login fail")


if __name__ == "__main__":
    # debug=True enables auto-reload and the Werkzeug debugger (dev only).
    app.run(debug=True)
