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

@application.route('/megabus')
def megabus_stuff():
    origin = request.args.get('orig')
    destination = request.args.get('dest')
    orig_city = db.session.query(City).filter(City.name==origin).first()
    dest_city = db.session.query(City).filter(City.name==destination).first()
    results = megabus.megabus(orig_city.megacode, dest_city.megacode, 4, 21, 2013) 
    return Response(json.dumps(results), mimetype='application/json')

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
