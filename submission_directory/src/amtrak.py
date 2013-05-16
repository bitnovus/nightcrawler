# curl -d "selOrigin=124_PRIN&selDestination=125_NEC&datepicker=04%2F26%2F2013&OriginDescription=Princeton&DestDescription=Princeton+Junction" 
# http://www.njtransit.com/sf/sf_servlet.srv?hdnPageAction=TrainSchedulesFrom 

import urllib2
import urllib
import re
import calendar

def sanitize_times(times):
	g = []
	for t in times:
		g.append(t[2:])
	return g

def sanitize_time(time):
	return time[2:]

def sanitize_price(price):
	return price[11:]

def sanitize_prices(prices):
	g = []
	for p in prices:
		g.append(p[11:])
	return g

def comp_times(time, hour, min):
  hour2 = int(get_hour(time))
  if time[time.find(':') + 4]=='P' and hour2!=12:
  	hour2 += 12
  if time[time.find(':') + 4] == 'A' and hour2==12:
  	hour2 -= 12
  min2 = int(get_min(time))
  if ((hour2< int(hour)) or (hour2 == int(hour) and min2 < int(min))):
  	return True
  return False

def get_hour(time):
  hour = int(time[0:time.find(":")])
  return hour

def get_min(time):
  colon = time.find(':')
  return int(time[colon+1: colon+3])

def mySearch(a, target):
	indices = []
	index = 0
	while index < len(a):
		if re.search(target, a[index]) is not None:
			indices.append(index)
		index += 1
	indices.append(len(a))
	return indices

def package_info(a, hour, minute, isArriving, link, payload):
	dictionaries = []
	indices = mySearch(a, "\$")

	for i in range(len(indices)):
		if i+1 < len(indices) and indices[i+1]==indices[i]+5:
			if isArriving and (comp_times(a[indices[i]+1], hour, minute) and comp_times(a[indices[i]+3], hour, minute)):
  				dictionaries.append(dict(price = a[indices[i]], departure = a[indices[i]+2], arrival = a[indices[i]+4], departure_time = a[indices[i]+1], arrival_time = a[indices[i]+3], carrier = "Amtrak", link = link, payload = payload))
  			elif ((isArriving is False) and ((comp_times(a[indices[i]+1], hour, minute) is False))):
  				dictionaries.append(dict(price = a[indices[i]], departure = a[indices[i]+2], arrival = a[indices[i]+4], departure_time = a[indices[i]+1], arrival_time = a[indices[i]+3], carrier = "Amtrak", link = link, payload = payload))
		elif i+1 < len(indices) and indices[i+1]==indices[i]+9:
			if isArriving and (comp_times(a[indices[i]+1], hour, minute) and comp_times(a[indices[i]+7], hour, minute)):
  				dictionaries.append([dict(price = a[indices[i]], departure = a[indices[i]+2], arrival = a[indices[i]+4], departure_time = a[indices[i]+1], arrival_time = a[indices[i]+3], carrier = "Amtrak", link = link, payload = payload), dict(price = a[indices[i]+5], departure = a[indices[i]+7], arrival = a[indices[i]+9], departure_time = a[indices[i]+6], arrival_time = a[indices[i]+8], carrier = "Amtrak", link = link, payload = payload, legs = 2)])
  			elif ((isArriving is False) and ((comp_times(a[indices[i]+1], hour, minute) is False))):
  				dictionaries.append([dict(price = a[indices[i]], departure = a[indices[i]+2], arrival = a[indices[i]+4], departure_time = a[indices[i]+1], arrival_time = a[indices[i]+3], carrier = "Amtrak", link = link, payload = payload, legs = 2), dict(price = a[indices[i]], departure = a[indices[i]+6], arrival = a[indices[i]+8], departure_time = a[indices[i]+5], arrival_time = a[indices[i]+7], carrier = "Amtrak", link = link, payload = payload, legs = 2)])
  	print dictionaries
  	return dictionaries 

def sanitize_loc(loc):
	r = loc.replace('+', ' ')
	r = r.replace('%2C', ',')
	r = r.replace('%28', '- ')
	r = r.replace('%29', '')
	return r

def sanitize_station(station):
	s = station[32:]
	s = s[:-20]
	return s

def amtrak(start, end, month, day, year, hour, min, isArriving):

	weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


	date = weekdays[int(calendar.weekday(int(year), int(month), int(day)))] + '%2C+' + months[int(month)-1] + '+' + str(day) + '%2C+' + str(year)
	tmp = "xwdf_origin=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FdepartLocation%2Fsearch&wdf_origin=" + start + "&xwdf_destination=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FarriveLocation%2Fsearch&wdf_destination=" + end + "&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate.date=" + date + "&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FallJourneyRequirements%2FnumberOfTravellers%5B%40key%3D%27Adult%27%5D=1&_handler%3Damtrak.presentation.handler.request.rail.AmtrakRailSearchRequestHandler%2F_xpath%3D%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D.x=24"
	link = "http://tickets.amtrak.com/itd/amtrak"
	html = urllib2.urlopen(link, tmp).read()

	start = sanitize_loc(start)
	end = sanitize_loc(end)

	# find all relevant pieces of information, then extract
	everything = re.findall("(: [0-9]*[0-9]:[0-9][0-9].*[AP]M)|(CartPrice.>\$[0-9]*\.[0-9][0-9])|(\n<!-- mp_trans_disable_start -->.*href)", html)
	temp = []
	for i in everything:
		for j in i:
			if j != "": temp.append(j)
	
	a = []

	for i in temp:
		if re.search(": [0-9]*[0-9]:[0-9][0-9].*[AP]M", str(i)) is not None: 
			a.append(sanitize_time(i))
		elif re.search("CartPrice.>\$[0-9]*\.[0-9][0-9]", str(i)) is not None: 
			a.append(sanitize_price(i))
		elif re.search("<!-- mp_trans_disable_start -->.*href", str(i)) is not None: 
			a.append(sanitize_station(i))
	
	p = package_info(a, hour, min, isArriving, link, tmp)
	#print p
	return p

if __name__ == '__main__':
	print amtrak('Trenton%2C+NJ+%28TRE%29', 'Boston+-+Back+Bay%2C+MA+%28BBY%29', '5', '30', '2013', '10', '30', False)
