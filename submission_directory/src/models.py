from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') \
        if os.environ.get('DATABASE_URL') else 'sqlite:///test.db'
db = SQLAlchemy(app)

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    state = db.Column(db.String(2))
    aircode = db.Column(db.String(5))
    megacode = db.Column(db.String(10))
    njcode = db.Column(db.String(30))
    njstation = db.Column(db.String(30))
    amcode = db.Column(db.String(60))

    def __init__(self, name, state, aircode, megacode):
        self.name = name
        self.state = state
        self.aircode = aircode
        self.megacode = megacode
        self.njcode = njcode
        self.amcode = amcode

    def __repr__(self):
        return '<City %r %r %r %r %r %r>' % (self.name, self.state, self.aircode, self.megacode, self.njcode, self.amcode)
