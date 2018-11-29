# coding=utf-8


from flask import Flask
# from flask_api import FlaskAPI

from app.api import configure_api
from app.external_apis import configure_external_apis
from app.models import db
from config import Env, configure_app, configure_db


def create_app(config_name):
    """
    Returns a new Flask app with all proper configurations ready.
    """
    app = Flask(__name__)
    configure_app(app, config_name)
    configure_db(app, db)
    configure_api(app)
    configure_external_apis(app)
    return app
