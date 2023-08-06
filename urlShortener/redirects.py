from flask import Blueprint, redirect
from urlShortener.db import get_db
from werkzeug.exceptions import abort

bp = Blueprint("redirects", __name__, url_prefix="/url")


@bp.route("/<suffix>")
def redirect_url(suffix: str):
    """
    Redirect to the stored URL against the random string assigned to it, or return 404 if not found in the database

    :param str suffix: URL variable referring to the randomly generated string assigned to a 'long' URL
    """
    url = get_db().execute("SELECT original_url FROM urls WHERE shortener_string = ?", (suffix,)).fetchone()

    if url is not None:
        return redirect(url[0])
    else:
        abort(404)
