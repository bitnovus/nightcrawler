from flask import Flask, render_template, jsonify, Response, request
from flask.ext.sqlalchemy import SQLAlchemy
from models import City, Route
import os, megabus, flights, json

#=========================================================

application = Flask(__name__)

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
application.debug=True

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') \
        if os.environ.get('DATABASE_URL') else 'sqlite:///test.db'

db = SQLAlchemy(application)
#=========================================================

@application.route('/')
def landing_page(name=None):
    return render_template('landing.html', name=name)

@application.route('/home')
def home_page(name=None):
    return render_template('home.html', name=name)

@application.route('/timeline')
def timeline(name=None):
    return render_template('timeline.html', name=name)

@application.route('/all')
def megabus_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    bus_results = megabus.megabus(orig_city.megacode, dest_city.megacode, month, day, year) 
    flight_results = flights.orbitz(orig_city.aircode, dest_city.aircode, month, day, year) 
    return Response(json.dumps(bus_results)+json.dumps(flight_results), mimetype='application/json')

@application.route('/megabus')
def megabus_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    print month + " " + day + " " + year
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = megabus.megabus(orig_city.megacode, dest_city.megacode, month, day, year) 

    print results
    return Response(json.dumps(results), mimetype='application/json')

@application.route('/flights')
def flight_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    print month + " " + day + " " + year
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = flights.orbitz(orig_city.aircode, dest_city.aircode, month, day, year) 
    return Response(json.dumps(results), mimetype='application/json')

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
