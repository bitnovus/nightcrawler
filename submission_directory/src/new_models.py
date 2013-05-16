from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os, graphConfiguration

app = Flask(__name__)
app.config.from_object(graphConfiguration.Config())

db = SQLAlchemy(app)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    orig_city = db.Column(db.String(30))
    orig_state = db.Column(db.String(2))
    dest_city = db.Column(db.String(30))
    dest_state = db.Column(db.String(2))

    provider = db.Column(db.String(30))
    method = db.Column(db.Integer(1))
    price = db.Column(db.Float())

    start_time = db.Column(db.DateTime(timezone=False))
    end_time = db.Column(db.DateTime(timezone=False))

    def __init__(self, orig_city, orig_state, dest_city, dest_state, provider, method, start_time, end_time):
        self.orig_city = orig_city
        self.orig_state = orig_state
        self.dest_city = dest_city
        self.dest_state = dest_state
        self.provider = provider
        self.method = method
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return '<Route %r %r>' % (self.orig.name, self.dest.name)
