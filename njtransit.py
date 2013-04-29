import urllib2
import urllib
import re

#r = requests.post("http://www.njtransit.com/sf/sf_servlet.srv?hdnPageAction=TrainSchedulesFrom", params=payload)
#curl -d "selOrigin=124_PRIN&selDestination=125_NEC&datepicker=4%2F26%2F2013&OriginDescription=Princeton&DestDescription=Princeton+Junction" http://www.njtransit.com/sf/sf_servlet.srv?hdnPageAction=TrainSchedulesFrom 

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

def package_info(times, price2, start, end, hour, minute, isArriving):
  dictionaries = []
  for j in range(len(times)/2):
  	if isArriving and (comp_times(times[2*j], hour, minute) and comp_times(times[2*j+1], hour, minute)):
  		dictionaries.append(dict(price = price2, departure = start, arrival = end, departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "NJ Transit"))
  	elif ((isArriving is False) and ((comp_times(times[2*j], hour, minute) is False))):
  		dictionaries.append(dict(price = price2, departure = start, arrival = end, departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "NJ Transit"))
  return dictionaries 

def sanitize_loc(loc):
	r = loc.replace('+', ' ')
	return r

def njtransit(start, end, month, day, year, hour, min, isArriving):

  date = str(month) + '%2F' + str(day) + '%2F' + str(year)
  payload = {'selOrigin': '124_PRIN', 
  'selDestination': '125_NEC', 
  'datepicker' : date, 
  'OriginDescription' : start, 
  'DestDescription' : end }

  req = urllib2.Request("http://www.njtransit.com/sf/sf_servlet.srv?hdnPageAction=TrainSchedulesFrom", urllib.urlencode(payload))
  res = urllib2.urlopen(req)
  html = res.read()

  times = re.findall("[0-9]*[0-9]:[0-9][0-9].*[AP]M", html)
  price = re.search("\$[0-9]*\.[0-9][0-9]", html).group(0)
  start = sanitize_loc(start)
  end = sanitize_loc(end)

  p = package_info(times, price, start, end, hour, min, isArriving)
  print p
  return p


if __name__ == '__main__':
	njtransit('Princeton', 'Princeton+Junction', '4', '30', '2013', '10', '30', False)