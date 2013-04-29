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

def package_info(times, prices, start, end, hour, minute, isArriving):
  dictionaries = []
  for j in range(len(prices)):
  	if isArriving and (comp_times(times[2*j], hour, minute) and comp_times(times[2*j+1], hour, minute)):
  		dictionaries.append(dict(price = prices[j], departure = start, arrival = end, departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "Amtrak"))
  	elif ((isArriving is False) and ((comp_times(times[2*j], hour, minute) is False))):
  		dictionaries.append(dict(price = prices[j], departure = start, arrival = end, departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "Amtrak"))
  return dictionaries 

def sanitize_loc(loc):
	r = loc.replace('+', ' ')
	r = r.replace('%2C', ',')
	r = r.replace('%28', '- ')
	r = r.replace('%29', '')
	return r

def amtrak(start, end, month, day, year, hour, min, isArriving):

	weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


	date = weekdays[int(calendar.weekday(int(year), int(month), int(day)))] + '%2C+' + months[int(month)] + '+' + str(day) + '%2C+' + str(year)
	tmp = "xwdf_origin=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FdepartLocation%2Fsearch&wdf_origin=" + start + "&xwdf_destination=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FarriveLocation%2Fsearch&wdf_destination=" + end + "&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate.date=" + date + "&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FallJourneyRequirements%2FnumberOfTravellers%5B%40key%3D%27Adult%27%5D=1&_handler%3Damtrak.presentation.handler.request.rail.AmtrakRailSearchRequestHandler%2F_xpath%3D%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D.x=24"

	html = urllib2.urlopen("http://tickets.amtrak.com/itd/amtrak", tmp).read()

	start = sanitize_loc(start)
	end = sanitize_loc(end)

	times = re.findall(": [0-9]*[0-9]:[0-9][0-9].*[AP]M", html)
	times = sanitize_times(times)

	prices = re.findall("CartPrice.>\$[0-9]*\.[0-9][0-9]", html)
	prices = sanitize_prices(prices)
	
	p = package_info(times, prices, start, end, hour, min, isArriving)
	print p
	return p

if __name__ == '__main__':
	amtrak('Trenton%2C+NJ+%28TRE%29', 'New+York+-+Penn+Station%2C+NY+%28NYP%29', '4', '30', '2013', '10', '30', False)