#the first two numbers are the stop_ids
#new york to trenton

def get_serviceID(month, day, year):
  f = open("calendar_dates.txt", "r")
  m = str(month)
  if len(m)==1: m = '0' + m
  d = str(day)
  if len(d)==1: d = '0' + d
  s = str(year)+m+d
  for line in f:
    if line.find(s)>0:
      tokDate = line.split(",")
  return tokDate[0]

def get_stopName(locNum):
  f = open("stops.txt", "r")
  lines = f.readlines()
  num = len(lines)
  for x in range(1,num):
    tok = lines[x].split(",")
    if int(tok[0])==int(locNum): return tok[2]

def get_validDay(serviceID, tripID):
  return True
  f = open("trips.txt", "r")
  lines = f.readlines()
  num = len(lines)
  for x in range(1,num):
    tok = lines[x].split(',')
    if tok[2]==tripID:
      if int(tok[1])!=int(serviceID): return False

def comp_times(time, hour, time):
  hour2 = int(get_hour(time))
  min2 = int(get_min(time))
  if (hour2<hour) or (hour2==hour and min2<min):
    return True
  else: return False

def get_hour(time)
  hour = int(time[0:time.find(':')])
  return hour

def get_min(time)
  colon = time.find(':')
  return int(time[colon + 1: colon + 3])

def sanitize_times(time):
  colon = time.find(':')
  if get_hour(time)>12:
    return (str(time-12) + time[colon+1:colon+3] + " PM")
  elif get_hour(time)==0:
    return (str(12) + time[colon+1:colon+3] + " AM")
  elif get_hour(time)==12:
    return (str(12) + time[colon+1:colon+3] + " PM")
  else
    return (time[0:colon+3] + " AM") 

def package_info(start, end, startTimes, endTimes, hour, minute, isArriving):
  i = len(startTimes)
  dictionaries = []
  for j in range(len(startTimes)):
    # 23 need both arrival and departure times to be before the given time
    if isArriving and (comp_times(startTimes[j], hour, minute) and comp_times(endTimes[j], hour, minute)):
      dictionaries.append(dict(price = "price", departure = get_stopName(start), arrival = get_stopName(end), departure_time = sanitize_times(startTimes[j]), arrival_time = sanitize_times(endTimes[j]), carrier = "NJ Transit"))
  return dictionaries

def njtransit(start, end, month, day, year, hour, minute, isArriving):
  startTimes = []
  endTimes = []
  f3 = open("routes.txt", "r")
  f4 = open("shapes.txt", "r")
  f5 = open("stop_times.txt", "r")
  f6 = open("stops.txt", "r")
  f7 = open("trips.txt", "r")
  lineStart = 1
  lineEnd = 0
  serviceID = get_serviceID(month, day, year)
  #look at stop times to make sure that they are on the same trip
  lines = f5.readlines()
  num = len(lines)
  for x in range(1,num):
    tokStop = lines[x].split(',')
    if int(tokStop[3])==int(start):
      if get_validDay(serviceID, tokStop[0]):
        for y in range(lineStart+1, num):
          tokStop2 = lines[y].split(',')
          if int(tokStop2[0])!=int(tokStop[0]): break
          #print tokStop2[3]
          if int(tokStop2[3])==int(end):
            startTimes.append(tokStop[1])
            endTimes.append(tokStop2[1])
          lineEnd += 1 
    lineStart += 1          
  p = package_info(start, end, startTimes, endTimes, hour, minute, isArriving)
  print p
  return p  

if __name__ == '__main__':
  njtransit(105, 148, 04, 30, 2013, 20, 30 True)
