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

def sanitize_middleCity(middleCity):
  city = middleCity[19:]
  city = city[:-10]
  return city

def get_min(time):
  colon = time.find(':')
  return int(time[colon+1: colon+3])

def package_info(times, price2, start, end, hour, minute, isArriving, link, payload):
  dictionaries = []
  for j in range(len(times)/2):
  	if isArriving and (comp_times(times[2*j], hour, minute) and comp_times(times[2*j+1], hour, minute)):
  		dictionaries.append(dict(price = price2, departure = start, arrival = end, departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "NJ Transit", link = link, payload = payload))
  	elif ((isArriving is False) and ((comp_times(times[2*j], hour, minute) is False))):
  		dictionaries.append(dict(price = price2, departure = start, arrival = end, departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "NJ Transit", link = link, payload = payload))
  return dictionaries 

def package_info_1stop(times, price2, middleCity, start, end, hour, minute, isArriving, link, payload):
  dictionaries = []
  for j in range(len(times)/4):
    if isArriving and (comp_times(times[4*j], hour, minute) and comp_times(times[4*j+3], hour, minute)):
      dictionaries.append([dict(price = price2, departure = start, arrival = middleCity, departure_time = times[4*j], arrival_time = times[4*j+1], carrier = "NJ Transit", link = link, payload = payload), dict(price = price2, departure = middleCity, arrival = end, departure_time = times[4*j+2], arrival_time = times[4*j+3], carrier = "NJ Transit", link = link, payload = payload)])
    elif ((isArriving is False) and ((comp_times(times[4*j], hour, minute) is False))):
      dictionaries.append([dict(price = price2, departure = start, arrival = middleCity, departure_time = times[4*j], arrival_time = times[4*j+1], carrier = "NJ Transit", link = link, payload = payload), dict(price = price2, departure = middleCity, arrival = end, departure_time = times[4*j+2], arrival_time = times[4*j+3], carrier = "NJ Transit", link = link, payload = payload)])
  return dictionaries 

def package_info_2stop(times, price2, middleCity1, middleCity2, start, end, hour, minute, isArriving, link, payload):
  dictionaries = []
  for j in range(len(times)/6):
    if isArriving and (comp_times(times[6*j], hour, minute) and comp_times(times[6*j+5], hour, minute)):
      dictionaries.append([dict(price = price2, departure = start, arrival = middleCity1, departure_time = times[6*j], arrival_time = times[6*j+1], carrier = "NJ Transit", link = link, payload = payload), dict(price = price2, departure = middleCity1, arrival = middleCity2, departure_time = times[6*j+2], arrival_time = times[6*j+3], carrier = "NJ Transit", link = link, payload = payload), dict(price = price2, departure = middleCity2, arrival = end, departure_time = times[6*j+4], arrival_time = times[6*j+5], carrier = "NJ Transit", link = link, payload = payload)])
    elif ((isArriving is False) and ((comp_times(times[6*j], hour, minute) is False))):
      dictionaries.append([dict(price = price2, departure = start, arrival = middleCity1, departure_time = times[6*j], arrival_time = times[6*j+1], carrier = "NJ Transit", link = link, payload = payload), dict(price = price2, departure = middleCity1, arrival = middleCity2, departure_time = times[6*j+2], arrival_time = times[6*j+3], carrier = "NJ Transit", link = link, payload = payload), dict(price = price2, departure = middleCity2, arrival = end, departure_time = times[6*j+4], arrival_time = times[6*j+5], carrier = "NJ Transit", link = link, payload = payload)])
  print dictionaries
  return dictionaries 

def sanitize_loc(loc):
	r = loc.replace('+', ' ')
	return r

def njtransit(start, end, codeStart, codeEnd, month, day, year, hour, min, isArriving):

  date = str(month) + '%2F' + str(day) + '%2F' + str(year)
  payload = {'selOrigin': codeStart, 
  'selDestination': codeEnd, 
  'datepicker' : date, 
  'OriginDescription' : start, 
  'DestDescription' : end }

  link = "http://www.njtransit.com/sf/sf_servlet.srv?hdnPageAction=TrainSchedulesFrom"

  req = urllib2.Request(link, urllib.urlencode(payload))
  res = urllib2.urlopen(req)
  html = res.read()
  #print html

  packets = re.findall('<td.align=.left..valign=.top..bgcolor=.#.......><span>.*td', html)
  new_packets = []
  index = 0
  for p in packets:
    if (re.search('minutes', p) is None):
      p2 = p[54:]
      p2 = p2[:-(len(p2) - p2.index("</span>"))]
      new_packets.append(p2)

  all_routes = []
  for i in range(0, len(new_packets) / 3):
    n = i * 3
    k = [new_packets[n], new_packets[n + 1], new_packets[n + 2]]
    all_routes.append(k)

  price = re.search("\$[0-9]*\.[0-9][0-9]", html).group(0)
  dictionaries = []
  for r in all_routes:
    if r[1] == '&nbsp;':
      dictionaries.append([dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(end), departure_time = r[0][: -1 * (len(r[0]) - r[0].index("<br>"))], arrival_time = r[2], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
    else:
      instances = re.findall("Arrive", r[1])
      length = len(instances)
      instances = re.split('<br>', r[1])
      if length == 1:
        dictionaries.append([dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(instances[1]), departure_time = r[0][: -1 * (len(r[0]) - r[0].index("<br>"))], arrival_time = instances[0][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload)), dict(price = price, departure = instances[1], arrival = end, departure_time = instances[2][7:], arrival_time = r[2], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
      elif length == 2:
        dictionaries.append(
          [dict(price = price, departure = sanitize_loc(start), arrival = sanitize_loc(instances[1]), departure_time = r[0][: -1 * (len(r[0]) - r[0].index("<br>"))], arrival_time = instances[0][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload)), 
          dict(price = price, departure = sanitize_loc(instances[1]), arrival = sanitize_loc(instances[4]), departure_time = instances[2][7:], arrival_time = instances[3][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload)),
          dict(price = price, departure = sanitize_loc(instances[1]), arrival = sanitize_loc(instances[4]), departure_time = instances[2][7:], arrival_time = instances[3][7:], carrier = "NJ Transit", link = link, payload = urllib.urlencode(payload))])
#  print dictionaries



  # if (re.search("<b>Transfer</b>", html) is None):
  #   times = re.findall("[0-9]*[0-9]:[0-9][0-9].[AP]M", html)
  #   price = re.search("\$[0-9]*\.[0-9][0-9]", html).group(0)
  #   start = sanitize_loc(start)
  #   end = sanitize_loc(end)
  #   p = package_info(times, price, start, end, hour, min, isArriving, link, urllib.urlencode(payload))
  #   #print p
  #   return p

  # elif (len(re.findall("<b>Transfer</b>", html)) == 1):
  #   times = re.findall("[0-9]*[0-9]:[0-9][0-9].[AP]M", html)
  #   price = re.search("\$[0-9]*\.[0-9][0-9]", html).group(0)
  #   middleCity = sanitize_middleCity(re.findall("Arrive.*Depart", html)[0])
  #   start = sanitize_loc(start)
  #   end = sanitize_loc(end)
  #   p = package_info_1stop(times, price, middleCity, start, end, hour, min, isArriving, link, urllib.urlencode(payload))
  #   #print p
  #   return p

  # elif (len(re.findall("<b>Transfer</b>", html)) == 2):
  #   times = re.findall("[0-9]*[0-9]:[0-9][0-9].[AP]M", html)
  #   price = re.search("\$[0-9]*\.[0-9][0-9]", html).group(0)
  #   middleCity1 = sanitize_middleCity(re.findall("Arrive.*Depart", html)[0])
  #   middleCity2 = sanitize_middleCity(re.findall("Arrive.*Depart", html)[1])
  #   start = sanitize_loc(start)
  #   end = sanitize_loc(end)
  #   p = package_info_2stop(times, price, middleCity1, middleCity2, start, end, hour, min, isArriving, link, urllib.urlencode(payload))
  #   #print p
  #   return p



if __name__ == '__main__':
	print njtransit('Newark+Airport', 'Princeton+Junction', '37953_NEC', '125_NEC', '5', '10', '2013', '23', '59', False)
