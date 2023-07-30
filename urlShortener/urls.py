import random
import string

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from urlShortener.auth import login_required
from urlShortener.db import get_db

bp = Blueprint("urls", __name__)


def generate_random_suffix(length: int) -> str:
    """
    Generate a random string of specified length containing upper and lower case ASCII letters
    :param length: Length of generated string
    """

    random_string: str = "".join(random.choice(string.ascii_letters) for _ in range(length))
    db_string = get_db().execute("SELECT * FROM urls WHERE shortener_string = ?", (random_string,)).fetchone()
    while db_string is not None:
        random_string = "".join(random.choice(string.ascii_letters) for _ in range(length))
        db_string = get_db().execute("SELECT * FROM urls WHERE shortener_string = ?", (random_string,)).fetchone()
    return random_string


@bp.route("/")
def index():
    return render_template("urls/index.html")


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        long_url: str = request.form["url"]
        error = None

        if long_url is None:
            error = "URL is required"

        if error is not None:
            flash(error)
        else:
            random_suffix: str = generate_random_suffix(5)

            db = get_db()
            db.execute(
                "INSERT INTO urls (originalUrl, shortener_string, creator_id) VALUES (?, ?, ?)",
                (long_url, random_suffix, g.user["id"])
            )
            db.commit()
            return redirect(url_for("urls.index"))
    return render_template("urls/create.html")
