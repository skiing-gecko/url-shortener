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


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as file:
        db.executescript(file.read().decode('"utf8'))


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialised the database")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
