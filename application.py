from flask import Flask, render_template, jsonify
import os

#=========================================================

application = Flask(__name__)

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
application.debug=True

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') \
        if os.environ.get('DATABASE_URL') else 'sqlite:///test.db'

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



if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
