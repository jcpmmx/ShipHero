# coding=utf-8


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()


class Carrier(db.Model):
    """
    Class that represents a carrier.
    
    This is in case we want to potentially manage multiple lists instead of a master list.
    """
    __tablename__ = 'carriers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    app_id = db.Column(db.String(255))
    app_token = db.Column(db.String(255))
    shipment_methods = db.Column(JSON)
    # Additional fields to make the model friendlier
    enabled = db.Column(db.Boolean, default=True)
    api_endpoint_url = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, name, app_id, app_token, shipment_methods, api_endpoint_url):
        self.name = name
        self.app_id = app_id
        self.app_token = app_token
        self.shipment_methods = shipment_methods
        self.api_endpoint_url = api_endpoint_url

    def __repr__(self):
        return '<Carrier: {}>'.format(self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def code(self):
        return self.name.strip().lower()

    @staticmethod
    def get_all():
        return Carrier.query.all()

    @staticmethod
    def get_all_enabled():
        return Carrier.query.filter_by(enabled=True)

