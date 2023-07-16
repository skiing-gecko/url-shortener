"Define and connect to the database"

import sqlite3
import click

from flask import current_app, g


def get_db():
    "Connect to database"

    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    "Close database connection"

    db = g.pop("db", None)

    if db is not None:
        db.close()
