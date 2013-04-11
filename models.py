from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    orig_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    dest_id = db.Column(db.Integer, db.ForeignKey('cities.id'))

    orig = db.relationship('City', backref = db.backref('routes', order_by = id), primaryjoin = "Route.orig_id == City.id")
    dest = db.relationship('City', primaryjoin = "Route.dest_id == City.id")

    provider = db.Column(db.String(30))
    method = db.Column(db.Integer(1))
    price = db.Column(db.Float())

    start_time = db.Column(db.DateTime(timezone=False))
    end_time = db.Column(db.DateTime(timezone=False))


    def __init__(self, orig, dest, provider, method):
        self.orig = orig
        self.dest = dest
        self.provider = provider
        self.method = method

    def __repr__(self):
        return '<Route %r %r>' % (self.orig.name, self.dest.name)

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    state = db.Column(db.String(2))
    aircode = db.Column(db.String(5))
    megacode = db.Column(db.String(10))

    def __init__(self, name, state, aircode, megacode):
        self.name = name
        self.state = state
        self.aircode = aircode
        self.megacode = megacode

    def __repr__(self):
        return '<City %r %r %r %r>' % (self.name, self.state, self.aircode, self.megacode)
