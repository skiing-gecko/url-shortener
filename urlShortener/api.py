from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort

from urlShortener.db import get_db
from urlShortener.urls import generate_random_suffix

from sqlite3 import IntegrityError

bp = Blueprint("api", __name__, url_prefix="/api/v1")


def authenticate_api(key: str):
    user = get_db().execute("SELECT * FROM user WHERE api_key = ?", (key,)).fetchone()

    if user is None:
        abort(401, description="Unauthorized")
    else:
        return user["id"]


@bp.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@bp.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e)), 401


@bp.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


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


@bp.route("/urls/<int:url_id>", methods=("PATCH",))
def update_url_by_id(url_id: int):
    key = request.headers.get("Authorization")

    user_id: str = authenticate_api(key)

    if (
        get_db()
        .execute("SELECT 1 WHERE EXISTS( SELECT 1 FROM urls WHERE id = ? )", (url_id,))
        .fetchone()
    ) is None:
        abort(404, description="Resource Not Found")

    if user_id is not None:
        try:
            name: str = request.json["url_name"]
            url: str = request.json["original_url"]

            db = get_db()
            db.execute(
                "UPDATE urls SET url_name = ?, original_url = ? WHERE id = ? AND creator_id = ?",
                (name, url, url_id, user_id),
            )
            db.commit()
            return "", 200
        except KeyError:
            abort(
                400,
                description="Bad Request. If you have entered the attribute names manually, try checking the spelling.",
            )


@bp.route("/urls", methods=("POST",))
def create_url():
    key = request.headers.get("Authorization")

    user_id: str = authenticate_api(key)

    if user_id is not None:
        try:
            url_name: str = request.json["url_name"]
            original_url: str = request.json["original_url"]

            try:
                shortener_string: str = request.json["shortener_string"]
            except KeyError:
                shortener_string = generate_random_suffix(5)

            try:
                db = get_db()
                db.execute(
                    "INSERT INTO urls (url_name, original_url, shortener_string, creator_id) VALUES (?, ?, ?, ?)",
                    (url_name, original_url, shortener_string, user_id),
                )
                db.commit()

                return "", 201
            except IntegrityError:
                abort(409)
        except KeyError:
            abort(
                400,
                description="Bad Request. If you have entered the attribute names manually, try checking the spelling.",
            )