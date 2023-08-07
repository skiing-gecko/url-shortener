from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort

from urlShortener.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api/v1")


def authenticate_api(key: str):
    user = get_db().execute("SELECT * FROM user WHERE api_key = ?", (key,)).fetchone()

    if user is None:
        abort(401)
    else:
        return user["id"]


@bp.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@bp.route("/urls", methods=("GET",))
def get_all_urls():
    key = request.headers.get("Authorization")

    user_id: str = authenticate_api(key)

    if user_id is not None:
        urls = (
            get_db()
            .execute(
                "SELECT url.id, url_name, original_url, shortener_string, created "
                "FROM urls url JOIN user usr ON url.creator_id = usr.id "
                "WHERE usr.id = ? "
                "ORDER BY created DESC",
                (user_id,),
            )
            .fetchall()
        )

        return {"urls": [dict(url) for url in urls]}


@bp.route("/urls/<int:url_id>", methods=("GET",))
def get_url_by_id(url_id: int):
    key = request.headers.get("Authorization")

    user_id: str = authenticate_api(key)

    if user_id is not None:
        url = (
            get_db()
            .execute(
                "SELECT url.id, url_name, original_url, shortener_string, created "
                "FROM urls url JOIN user usr ON url.creator_id = usr.id "
                "WHERE usr.id = ? AND url.id = ?"
                "ORDER BY created DESC",
                (user_id, url_id),
            )
            .fetchone()
        )
        if url is not None:
            return dict(url)
        abort(404, description="Resource Not Found")


@bp.route("/urls/<int:url_id>", methods=("DELETE",))
def delete_url_by_id(url_id: int):
    key = request.headers.get("Authorization")

    user_id: str = authenticate_api(key)

    if user_id is not None:
        db = get_db()
        db.execute(
            "DELETE FROM urls WHERE id = ? AND creator_id = ?", (url_id, user_id)
        )
        db.commit()
        return "", 204
