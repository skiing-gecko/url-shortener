import sqlite3

import pytest
from urlShortener.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        # Check is the same connection
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as error:
        db.execute("SELECT 1")

    assert "closed" in str(error.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def mock_init_db():
        Recorder.called = True

    monkeypatch.setattr("urlShortener.db.init_db", mock_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialised" in result.output
    assert Recorder.called
