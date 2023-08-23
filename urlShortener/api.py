from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort

from urlShortener.db import get_db
from urlShortener.urls import generate_random_suffix

from sqlite3 import IntegrityError

bp = Blueprint("api", __name__, url_prefix="/api/v0.1.0")


def authenticate_api(key: str):
    user = get_db().execute("SELECT * FROM user WHERE api_key = ?", (key,)).fetchone()

    if user is None:
        abort(
            401,
            description="Try checking that an API key has been supplied, and that it is spelled correctly.",
        )
    else:
        return user["id"]


@bp.errorhandler(400)
@bp.errorhandler(401)
@bp.errorhandler(404)
@bp.errorhandler(415)
@bp.errorhandler(500)
def http_error_handler(err):
    return jsonify(error=str(err)), err.code


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

        if bool(urls):
            return {"urls": [dict(url) for url in urls]}
        else:
            abort(404, description="No URLs found")


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
        abort(404, description="A URL with this ID was not found")


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
        except (KeyError, TypeError):
            abort(
                400,
                description="Try checking the spelling, and that all required attributes are present.",
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
                abort(
                    409,
                    description="A URL with this shortener string already exists. Please try again with a different "
                    "string, or remove the shortener_string attribute to receive a random string.",
                )
        except KeyError:
            abort(
                400,
                description="Bad Request. If you have entered the attribute names manually, try checking the spelling.",
            )
