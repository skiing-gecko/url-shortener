from flask import Blueprint, redirect
from urlShortener.db import get_db

bp = Blueprint("redirects", __name__, url_prefix="/url")


@bp.route("/<suffix>")
def redirect_url(suffix: str):
    url = get_db().execute("SELECT originalUrl FROM urls WHERE shortener_string = ?", (suffix,)).fetchone()
    return redirect(url[0])
