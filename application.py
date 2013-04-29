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

@application.route('/cities')
def all_cities():
    cities = db.session.query(City.name).all()
    results = []
    for city_sublist in cities:
        for city in city_sublist:
            results.append(city)

    return Response(json.dumps(results), mimetype='application/json')

@application.route('/all')
def all_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    isArriv = (request.args.get('arriveby') == 'true')
    try:
        hour = int(request.args.get('hour'))
    except:
	if isArriv:
	    hour = 30
	else:
	    hour = 0
    try:
        minute = int(request.args.get('minute'))
    except:
        minute = 0
    """print type(isArriv)
    print type(hour)
    print type(minute)
    print request.args"""
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    bus_results = megabus.megabus(orig_city.megacode, dest_city.megacode, month, day, year, hour, minute, isArriv)
    flight_results = flights.orbitz(orig_city.aircode, dest_city.aircode, month, day, year, hour, minute, isArriv)
    nj_results = njtransit.njtransit(orig_city.njcode, dest_city.njcode, month, day, year, hour, minute, isArriv)
    am_results = amtrak.amtrak(orig_city.amcode, dest_city.amcode, month, day, year, hour, minute, isArriv)
    #print bus_results
    #print flight_results
    #print hour
    #print minute
    #print megabus.megabus(89, 123, 4, 25, 2013, 13, 30, False)
    total_results = bus_results + flight_results + nj_results + am_results
    return Response(json.dumps(total_results), mimetype='application/json')

@application.route('/megabus')
def megabus_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    hour = request.args.get('hour')
    minute = request.args.get('minute')
    isArriv = request.args.get('arriveby')
    #print month + " " + day + " " + year
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = megabus.megabus(orig_city.megacode, dest_city.megacode, month, day, year, hour, minute, isArriv)

    #print results
    return Response(json.dumps(results), mimetype='application/json')

@application.route('/flights')
def flight_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    hour = request.args.get('hour')
    minute = request.args.get('minute')
    isArriv = request.args.get('arriveby')
    #print month + " " + day + " " + year
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = flights.orbitz(orig_city.aircode, dest_city.aircode, month, day, year, hour, minute, isArriv) 
    return Response(json.dumps(results), mimetype='application/json')

@application.route('/njtransit')
def flight_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    hour = request.args.get('hour')
    minute = request.args.get('minute')
    isArriv = request.args.get('arriveby')
    #print month + " " + day + " " + year
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = njtransit.njtransit(orig_city.njcode, dest_city.njcode, month, day, year, hour, minute, isArriv) 
    return Response(json.dumps(results), mimetype='application/json')

@application.route('/amtrak')
def flight_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    month = request.args.get('month')
    day = request.args.get('day') 
    year = request.args.get('year')
    hour = request.args.get('hour')
    minute = request.args.get('minute')
    isArriv = request.args.get('arriveby')
    #print month + " " + day + " " + year
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = amtrak.amtrak(orig_city.amcode, dest_city.amcode, month, day, year, hour, minute, isArriv) 
    return Response(json.dumps(results), mimetype='application/json')

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
