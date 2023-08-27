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

    random_string: str = "".join(
        random.choice(string.ascii_letters) for _ in range(length)
    )
    suffix_is_unique: bool = check_unique_suffix(random_string)

    while not suffix_is_unique:
        random_string = "".join(
            random.choice(string.ascii_letters) for _ in range(length)
        )
        suffix_is_unique = check_unique_suffix(random_string)
    return random_string


def check_unique_suffix(suffix: str) -> bool:
    """
    Return True if the suffix is not in the database, False otherwise
    """

    db_string = (
        get_db()
        .execute("SELECT * FROM urls WHERE shortener_string = ?", (suffix,))
        .fetchone()
    )
    if db_string is None:
        return True
    return False


def page_not_found(e):
    return render_template("404.html"), e.code


@bp.route("/")
def index():
    urls = None

    if g.user is not None:
        urls = (
            get_db()
            .execute(
                "SELECT url.id, url_name, original_url, shortener_string, creator_id "
                "FROM urls url JOIN user usr ON url.creator_id = usr.id "
                "WHERE usr.id = ? "
                "ORDER BY created DESC",
                (g.user["id"],),
            )
            .fetchall()
        )
    return render_template("urls/index.html", urls=urls)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        url_name: str = request.form["url_name"]
        long_url: str = request.form["url"]
        custom_suffix: str = request.form["extension"]
        error: None | str = None

        if long_url is None:
            error = "URL is required"

        if custom_suffix != "":
            if not check_unique_suffix(custom_suffix):
                error = "That URL extension is not available"

        if error is not None:
            flash(error)
        else:
            if custom_suffix == "":
                suffix: str = generate_random_suffix(5)
            else:
                suffix = custom_suffix

            db = get_db()
            db.execute(
                "INSERT INTO urls (url_name, original_url, shortener_string, creator_id) VALUES (?, ?, ?, ?)",
                (url_name, long_url, suffix, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("urls.index"))
    return render_template("urls/create.html")


def get_url(url_id: int, check_creator: bool = True):
    """
    :param int url_id: ID of the URL to get
    :param bool check_creator: If true, check to ensure the user performing the operation is the creator of the URL
    """

    url = (
        get_db()
        .execute(
            "SELECT url.id, creator_id, created, url_name, shortener_string, original_url "
            "FROM urls url JOIN user u ON url.creator_id = u.id "
            "WHERE url.id = ?",
            (url_id,),
        )
        .fetchone()
    )

    if url is None:
        abort(404, f"URL ID {url_id} does not exist")

    if check_creator and url["creator_id"] != g.user["id"]:
        abort(403)

    return url


@bp.route("/<int:url_id>/delete", methods=("POST",))
@login_required
def delete(url_id: int):
    """
    :param int url_id: ID of the URL to be deleted
    """

    get_url(url_id)
    db = get_db()
    db.execute("DELETE FROM urls WHERE id = ?", (url_id,))
    db.commit()

    return redirect(url_for("urls.index"))
