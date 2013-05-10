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
  #print time
  if re.search("Arrive", time) is not None:
    time = time[7:]
  #print time
  hour = int(time[time.find(":") - 2:time.find(":")])
  return hour

def sanitize_middleCity(middleCity):
  city = middleCity[19:]
  city = city[:-10]
  return city

def get_min(time):
  colon = time.find(':')
  return int(time[colon+1: colon+3])

def sanitize_loc(loc):
	r = loc.replace('+', ' ')
	return r

def njtransit(start, end, codeStart, codeEnd, month, day, year, hour, min, isArriving):
  #date = str(month) + '%2F' + str(day) + '%2F' + str(year)
  #date = "05/11/2013"
  if len(month) == 1:
    month = "0" + month
  date = month + "/" + day + "/" + year
  payload = {'selOrigin': codeStart, 
  'selDestination': codeEnd, 
  'datepicker' : date, 
  'OriginDescription' : start, 
  'DestDescription' : end }

  link = "http://www.njtransit.com/sf/sf_servlet.srv?hdnPageAction=TrainSchedulesFrom"

  req = urllib2.Request(link, urllib.urlencode(payload))
  res = urllib2.urlopen(req)
  html = res.read()
  price = re.search("\$[0-9]*\.[0-9][0-9]", html).group(0)

  packets = re.findall('<td.align=.left..valign=.top..bgcolor=.#.......><span>.*td', html)
  new_packets = []
  for p in packets:
    if (re.search('minutes', p) is None):
      p2 = p[54:]
      p2 = p2[:-(len(p2) - p2.index("</span>"))]
      new_packets.append(p2)

  if re.match("Arrive", new_packets[1]) is None:
    single_stop = []
    for i in range(0, len(new_packets)/2):
      single_stop.append([dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(end), 
        departure_time = new_packets[2 * i][: -1 * (len(new_packets[2 * i]) - new_packets[2 * i].index("<br>"))], 
        arrival_time = new_packets[2 * i+1], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
    return single_stop


  all_routes = []

  i = 0
  while i < len(new_packets):
    if i == len(new_packets) - 1:
      break
    if re.search("&nbsp;", new_packets[i+2]) is not None or re.search("Arrive", new_packets[i + 2]) is not None:
      k = [new_packets[i], new_packets[i + 1] + new_packets[i+2], new_packets[i + 3]]
      all_routes.append(k)
      i += 4
    else:
      k = [new_packets[i], new_packets[i + 1], new_packets[i + 2]]
      all_routes.append(k)
      i += 3


  
  dictionaries = []
  for r in all_routes:
    if r[1] == '&nbsp;':
      dictionaries.append([dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(end), departure_time = r[0][: -1 * (len(r[0]) - r[0].index("<br>"))], arrival_time = r[2], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
    else:
      instances = re.findall("Arrive", r[1])
      length = len(instances)
      instances = re.split('<br>', r[1])

      if length == 1:
        dictionaries.append([dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(instances[1]), departure_time = r[0][: -1 * (len(r[0]) - r[0].index("<br>"))], arrival_time = instances[0][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload)), dict(price = price, departure = instances[1], arrival = sanitize_loc(end), departure_time = instances[2][7:], arrival_time = r[2], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
      elif length == 2:
        dictionaries.append(
          [dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(instances[1]), departure_time = r[0][: -1 * (len(r[0]) - r[0].index("<br>"))], arrival_time = instances[0][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload)), 
          dict(price = price, departure = sanitize_loc(instances[1]), arrival = sanitize_loc(instances[4]), departure_time = instances[2][7:], arrival_time = instances[3][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload)),
          dict(price = price, departure = sanitize_loc(instances[1]), arrival = sanitize_loc(instances[4]), departure_time = instances[2][7:], arrival_time = instances[3][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
  new_dictionaries = []

  for d in dictionaries:
    if isArriving and (comp_times(d[0].get("departure_time"), hour, min) and 
      comp_times(d[len(d) - 1].get("arrival_time"), hour, min)):
      new_dictionaries.append(d)
    elif ((isArriving is False) and (comp_times(d[0].get("departure_time"), hour, min) is False)):
      new_dictionaries.append(d)

  return new_dictionaries

if __name__ == '__main__':

  #print njtransit('Newark+Penn+Station', 'Princeton', '107_NEC', '124_PRIN', '5', '11', '2013', '23', '59', True)

	#print njtransit('Newark+Penn+Station', 'Princeton+Junction', '107_NEC', '125_NEC', '5', '11', '2013', '23', '59', True)
  #print njtransit('New+York+Penn+Station', 'Princeton+Junction', '105_BNTN', '125_NEC', '5', '11', '2013', '23', '59', True)
  #print njtransit('Newark+Penn+Station', 'Princeton', '107_NEC', '124_PRIN', '5', '11', '2013', '23', '59', True)
  #print njtransit('Princeton+Junction', 'Princeton', '125_NEC', '124_PRIN', '5', '11', '2013', '23', '59', True)
  #print njtransit('New+York+Penn+Station', 'Princeton', '105_BNTN', '124_PRIN', '5', '11', '2013', '23', '59', True)
  #print njtransit('Princeton', 'Newark+Penn+Station', '124_PRIN', '107_NEC', '5', '11', '2013', '23', '59', True)
  print njtransit('Princeton', 'Newark+Airport', '124_PRIN', '37953_NEC', '5', '11', '2013', '23', '59', True)
