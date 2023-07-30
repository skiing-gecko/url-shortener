"""Create Flask application"""

# Based on Flask tutorial: https://flask.palletsprojects.com/en/2.3.x/tutorial/

import os
from flask import Flask


def create_app(test_config=None):
    """Create Flask app"""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "urlShortener.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "hello, world!"

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import urls

    app.register_blueprint(urls.bp)
    app.add_url_rule("/", endpoint="index")
    app.register_error_handler(404, urls.page_not_found)

    return app
