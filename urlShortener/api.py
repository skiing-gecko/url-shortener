from flask import Blueprint, redirect
from werkzeug.exceptions import abort

from urlShortener.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api/v1")


@bp.route("/urls", methods=("GET",))
def get_all_urls():
    pass
