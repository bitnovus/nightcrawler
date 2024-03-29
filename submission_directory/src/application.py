from flask import Flask, render_template, jsonify, Response, request, Markup, send_from_directory, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from models import City
import os, megabus, flights, json, njtransit, amtrak, re
from multiprocessing.pool import ThreadPool
from werkzeug.routing import BaseConverter

#=========================================================

application = Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') \
        if os.environ.get('DATABASE_URL') else '**REDACTED**'

        #if os.environ.get('DATABASE_URL') else 'sqlite:///test.db'

db = SQLAlchemy(application)

pool = ThreadPool(processes=14)
#=========================================================

@application.route('/about')
def landing_page(name=None):
    return render_template('landing.html', name=name)

@application.route('/')
def redirect_to_home(code=301):
    return redirect("home", code)

@application.route('/home')
def home_page(name=None):
    return render_template('home.html', name=name)

@application.route('/timeline')
def timeline(name=None):
    return render_template('timeline.html', name=name)

@application.route('/map')
def show_map(name=None):
    test_stops = ["Princeton Junction, NJ", "Newark Airport, NJ", "Logan Airport, MA"]
    test_modes = ["DRIVING", "FLYING"]

    input_stops = request.args.get('stops')
    input_modes = request.args.get('modes')
    origstate = request.args.get('origstate')
    deststate = request.args.get('deststate')
    origcity = request.args.get('origcity')
    destcity = request.args.get('destcity')

    regex = re.compile("(\'.*?\')")
    print input_stops

    old_stops_list = regex.findall(input_stops)
    modes_list = regex.findall(input_modes)

    new_stops_list = []

    #print old_stops_list

    for i in range(0, len(old_stops_list)):
        temp_stop = '"'
        temp_stop += old_stops_list[i][1:-1]
        if modes_list[min(i, len(modes_list)-1)] != "\'TRANSIT\'":
            print i
            temp_stop += ' '
            if i == 0:
                temp_stop += origcity
                temp_stop += ','
                temp_stop += origstate
            elif i == len(old_stops_list)-1:
                temp_stop += destcity
                temp_stop += ','
                temp_stop += deststate

        temp_stop = temp_stop.replace("b/t", "")
        temp_stop += '"'
        new_stops_list.append(temp_stop)

    stops = ','.join(new_stops_list)
    modes = ','.join(modes_list)

    stops = "[" + stops + "]"
    modes = "[" + modes + "]"

    if not stops:
        stops = test_stops
    if not modes:
        modes = test_modes

    #print stops
    #print modes

    return render_template('map.html', stops=Markup(stops), modes=Markup(modes))

@application.route('/cities')
def all_cities():
    cities = db.session.query(City.name).all()
    states = db.session.query(City.state).all()
    results = []

    for i in range(len(cities)):
        results.append(cities[i][0] + ", " + states[i][0])

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

    """if origin == "Princeton":
	#Princeton to Princeton Junction
	pj = db.session.query(City).filter(City.name=='Princeton Junction').first()
	p_result1 = pool.apply_async(njtransit.njtransit, (orig_city.njstation, pj.njstation, orig_city.njcode, pj.njcode, month, day, year, hour, minute, isArriv))
        p_result2 = pool.apply_async(amtrak.amtrak, (pj.amcode, dest_city.amcode, month, day, year, hour, minute, isArriv))
    else:
	p_result1 = []
	p_result2 = []"""

    if orig_city.aircode.find("*") != -1:
        # get airport city
	orig_city2 = db.session.query(City).filter(City.name==get_city(orig_city.aircode[1:])).first()
        leg1_result1 = pool.apply_async(megabus.megabus, (orig_city.megacode, orig_city2.megacode, month, day, year, hour, minute, isArriv))
        leg1_result2 = pool.apply_async(njtransit.njtransit, (orig_city.njstation, orig_city2.njstation, orig_city.njcode, orig_city2.njcode, month, day, year, hour, minute, isArriv))
        leg1_result3 = pool.apply_async(amtrak.amtrak, (orig_city.amcode, orig_city2.amcode, month, day, year, hour, minute, isArriv))
    else:
	orig_city2 = orig_city
	leg1_result1 = []
	leg1_result2 = []
	leg1_result3 = []

    if dest_city.aircode.find("*") != -1:
	#get airport city
	dest_city2 = db.session.query(City).filter(City.name==get_city(dest_city.aircode[1:])).first()
        leg3_result1 = pool.apply_async(megabus.megabus, (dest_city2.megacode, dest_city.megacode, month, day, year, hour, minute, isArriv))
        leg3_result2 = pool.apply_async(njtransit.njtransit, (dest_city2.njstation, dest_city.njstation, dest_city2.njcode, dest_city.njcode, month, day, year, hour, minute, isArriv))
        leg3_result3 = pool.apply_async(amtrak.amtrak, (dest_city2.amcode, dest_city.amcode, month, day, year, hour, minute, isArriv))
    else:
	dest_city2 = dest_city
	leg3_result1 = []
	leg3_result2 = []
	leg3_result3 = []

    # flight results
    flight_result = pool.apply_async(flights.orbitz, (orig_city2.aircode, dest_city2.aircode, month, day, year, hour, minute, isArriv))

    async_result1 = pool.apply_async(megabus.megabus, (orig_city.megacode, dest_city.megacode, month, day, year, hour, minute, isArriv))
    #async_result2 = pool.apply_async(flights.orbitz, (orig_city.aircode, dest_city.aircode, month, day, year, hour, minute, isArriv))
    async_result3 = pool.apply_async(njtransit.njtransit, (orig_city.njstation, dest_city.njstation, orig_city.njcode, dest_city.njcode, month, day, year, hour, minute, isArriv))
    async_result4 = pool.apply_async(amtrak.amtrak, (orig_city.amcode, dest_city.amcode, month, day, year, hour, minute, isArriv))

    leg1 = []
    leg2 = []
    leg3 = []

    try:
	leg1_1 = leg1_result1.get()
    except:
	leg1_1 = []

    try:
	leg1_2 = leg1_result2.get()
    except:
	leg1_2 = []
    try:
	leg1_3 = leg1_result3.get()
    except:
	leg1_3 = []

    leg1 = leg1_1 + leg1_2 + leg1_3

    try:
	leg2 = flight_result.get()
    except:
	leg2 = []
    flight_results = leg2

    try:
	leg3_1 = leg3_result1.get()
    except:
	leg3_1 = []
    try:
	leg3_2 = leg3_result2.get()
    except:
        leg3_2 = []
    try:
	leg3_3 = leg3_result3.get()
    except:
	leg3_3 = []

    leg3 = leg3_1 + leg3_2 + leg3_3

    """try:
	princeton_leg1 = p_result1.get()
    except:
	princeton_leg1 = []

    try:
	princeton_leg2 = p_result2.get()
    except:
	princeton_leg2 = []"""

    try:
        bus_results = async_result1.get()
    except:
        bus_results = []

    #try:
    #    flight_results = async_result2.get()
    #except:
    #    flight_results = []

    try:
        nj_results = async_result3.get()
    except:
        nj_results = []

    try:
        am_results = async_result4.get()
    except:
        am_results = []

    #print bus_results
    #print flight_results
    #print hour
    #print minute
    #print megabus.megabus(89, 123, 4, 25, 2013, 13, 30, False)
    #total_results = bus_results + flight_results + nj_results + am_results

    #total_results = bus_results + nj_results + am_results
    #if not (dest_city != dest_city2 and leg3 == []) and not (orig_city != orig_city2 and leg1 == []):
    #    total_results += combine(leg1, leg2, leg3)
    total_results = bus_results + nj_results + am_results
    if not (dest_city != dest_city2 and leg3 == []) and not (orig_city != orig_city2 and leg1 == []):
        total_results += combine(leg1, leg2, leg3)

    #print princeton_leg1
    #print princeton_leg2
    #if princeton_leg1 != [] and princeton_leg2 != []:
        #total_results += combine(princeton_leg1, princeton_leg2, [])
    return Response(json.dumps(total_results), mimetype='application/json')

def combine(leg1, leg2, leg3):
    if leg1 == [] and leg3 == []:
	return leg2
    results = []
    for flight in leg2:
	result = []
	best1 = []
	best3 = []
	if leg1 != []:
	    best1 = get_best_leg1(leg1, flight)
	    if best1 == []:
		continue
	if leg3 != []:
            best3 = get_best_leg3(leg3, flight)
	    if best3 == []:
		continue
	if best1 != []:
	    result.append(best1)
	result.append(flight)
	if best3 != []:
	    result.append(best3)

	first = result[0]
	if str(type(first)).find("list") != -1:
	    first = first[0]
	t1 = first['departure_time']

	last = result[len(result)-1]
	if str(type(last)).find("list") != -1:
	    last = last[len(last)-1]
	t2 = last['arrival_time']
	d = [{'arrival_time':t2, 'departure_time':t1}]
	result = d + result
	results.append(result)
	
    return results


def get_best_leg1(leg1, flight):
    flight_start = time_to_minutes(flight, True)
    best = []
    best_time = 1000000
    for r in leg1:
	end = time_to_minutes(r, False)
	if end + 60 < flight_start and flight_start - end < best_time:
            best = r
	    best_time = flight_start - end
    return best

def get_best_leg3(leg3, flight):
    flight_end = time_to_minutes(flight, False)
    best = []
    best_time = 1000000
    for r in leg3:
	start = time_to_minutes(r, True)
	if start > flight_end + 60 and start - flight_end < best_time:
            best = r
	    best_time = start - flight_end
    return best

def time_to_minutes(record, departure):
    if str(type(record)).find("list") != -1:
	# multiple stops
	first = record[0]
	last = record[len(record)-1]
    else:
	first = record
	last = record
    departure_hour = get_hour(first['departure_time'])
    departure_minute = get_minute(first['departure_time'])
    departure_in_minutes = departure_hour * 60 + departure_minute
    if departure:
	return departure_in_minutes
    arrival_hour = get_hour(last['arrival_time'])
    arrival_minute = get_minute(last['arrival_time'])
    arrival_in_minutes = arrival_hour * 60 + arrival_minute
    if arrival_in_minutes < departure_in_minutes:
	arrival_in_minutes += 24*60
    return arrival_in_minutes


def get_hour(time):
    hour = int(time[0:time.find(':')])
    if hour == 12:
        hour = 0
    if time.find("PM") != -1:
        hour += 12
    return hour

def get_minute(time):
    colon = time.find(':')
    return int(time[colon+1:colon+3])

def get_city(code):
    return airCodes[code]

# a list of the airport codes
airCodes = {'ALB':'Albany', 'ABE':'Allentown', 'BWI':'Baltimore', 'BGR':'Bangor', 'BOS':'Boston', 'BUF':'Buffalo', 'MDT':'Harrisburg', 'BDL':'Hartford', 'ISP':'Islip', 'EEN':'Keene', 'MHT':'Manchester', 'JFK':'New York', 'LGA':'New York 2', 'EWR':'Newark Airport', 'SWF':'Newburgh', 'PHL':'Philadelphia', 'PIT':'Pittsburg', 'SYR':'Syracuse', 'DCA':'Washington', 'IAD':'Washington 2', 'HPN':'Westchester', 'AVP':'Wilkes Barre', 'ORH':'Worcester', 'PVD':'Providence', 'HVN':'New Haven', 'LEB':'Lebanon'}

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
def njtransit_stuff():
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
    results = njtransit.njtransit(orig_city.njstation, dest_city.njstation, orig_city.njcode, dest_city.njcode, month, day, year, hour, minute, isArriv) 
    return Response(json.dumps(results), mimetype='application/json')

@application.route('/amtrak')
def amtrak_stuff():
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

@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
@application.route('/timeline.html')
def sub_timeline():
    return send_from_directory(os.path.join(application.root_path, 'submission_directory'), 'timeline.html', mimetype='text/html')

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

application.url_map.converters['regex'] = RegexConverter
@application.route('/<regex("[a-zA-Z0-9]+.png"):picName>')
def image_routes(picName):
    return send_from_directory(os.path.join(application.root_path, 'submission_directory'), picName, mimetype='image/png')

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=False)
