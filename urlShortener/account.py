from flask import Blueprint, g, render_template, request
from werkzeug.exceptions import abort

from urlShortener.auth import login_required
from urlShortener.db import get_db

bp = Blueprint("account", __name__, url_prefix="/account")


@bp.route("/", methods=("GET",))
@login_required
def account():
    return render_template("account/account.html")
