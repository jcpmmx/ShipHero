# coding=utf-8


import os
from enum import Enum

from sqlalchemy.exc import ProgrammingError

from app.models import Carrier

CARRIERS_DATA = [
    {
        'name': 'Fedex',
        'app_id': 'FEDEXID',
        'app_token': 'FEDEXTKN',
        'shipment_methods': {'cheap': 'fdxchp', 'regular': 'fdxreg', 'express': 'fdxexp'},
        'api_endpoint_url': '/mock/fedex/shippingcosts',
    },
    {
        'name': 'UPS',
        'app_id': 'UPSID',
        'app_token': 'UPSTKN',
        'shipment_methods': {'cheap': 'upschp', 'regular': 'upsreg', 'express': 'upsexp'},
        'api_endpoint_url': '/mock/ups/shippingcosts',
    },
]


class Env(Enum):
    """
    Enum that stores all possible envs.
    """
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    PRODUCTION = 'production'


class BaseConfig(object):
    """
    Default configurations for all envs.
    """
    DEBUG = True
    TESTING = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/shiphero'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FAKEJSON_API_ENDPOINT = 'https://app.fakejson.com/q'
    FAKEJSON_API_TOKEN = '<EDITED>'


class DevelopmentConfig(BaseConfig):
    """
    Development-only configurations.
    """
    ENV = Env.DEVELOPMENT


class TestingConfig(BaseConfig):
    """
    Testing-only configurations.
    """
    ENV = Env.TESTING
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/shiphero_test'


class ProductionConfig(BaseConfig):
    """
    Production-only configurations.
    """
    ENV = Env.PRODUCTION
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


def configure_app(app, target_env):
    """
    Sets all configurations in the given Flask app using a valid target environment (given either as a str or as a valid
    Env value).
    """
    _CONFIG_ENV_MAPPING = {
        Env.DEVELOPMENT: DevelopmentConfig,
        Env.TESTING: TestingConfig,
        Env.PRODUCTION: ProductionConfig,
    }
    if isinstance(target_env, str):
        try:
            target_env = Env(target_env)
        except ValueError:
            target_env = Env.DEVELOPMENT

    config_obj = _CONFIG_ENV_MAPPING[target_env]
    app.config.from_object(config_obj)


def configure_db(app, db):
    """
    Links together the given Flask app and the SQLAlchemy instance.
    It also loads some initial data.
    """
    db.init_app(app)
    with app.app_context():
        load_initial_db_data(app, db)


def load_initial_db_data(app, db):
    """
    Loads all required initial data to the given DB.
    """
    # Checking if we have carriers data
    try:
        if not db.session.query(Carrier).first():
            for carrier_data in CARRIERS_DATA:
                carrier = Carrier(**carrier_data)
                db.session.add(carrier)
            db.session.commit()
    except ProgrammingError:
        pass  # DB is empty, no tables yet
