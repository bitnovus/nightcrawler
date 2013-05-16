#!/bin/env python
import urllib2, re
from multiprocessing.pool import ThreadPool

def sanitize_departures(departures):
  g = []
  for d in departures:
    s = re.sub(r"ALBACORE\t\t\t\t\t\t\t\t", "", d)
    s = re.sub("\rAARDVARK", "", s)
    g.append(s)
  return g

def sanitize_carriers(carriers):
  g = []
  for c in carriers:
    s = re.sub(r"\t\t\t\t\t\t\t\t\t\t\t", "", c)
    s = re.sub(" </strong>", "", s)
    g.append(s)
  return g

def sanitize_prices(prices):
  g = []
  for p in prices:
    s = re.sub('money-symbol\">\$</span>', "", p)
    s = re.sub('<span class=\"money-cents\">', "", s)
    s = re.sub(',', "", s)
    s = '$' + s
    g.append(s)
  return g

def sanitize_times(times):
  g = []
  for t in times:
    s = re.sub(' </span>', "", t)
    g.append(s)
  return g

# returns true if time is before hour and minute
# hours are between 0 and 23 when they are passed in
def comp_times(time, hour, min):
  hour2 = int(get_hour(time))
  if time[time.find(':') + 4] == 'P' and hour2!=12:
    hour2 = hour2 + 12
  if time[time.find(':') + 4] == 'A' and hour2==12:
    hour2 = hour2 - 12
  min2 = int(get_min(time))
  if (hour2 < hour) or (hour2==hour and min2 < min):
    return True
  else: return False

def get_hour(time):
  hour = int(time[0:time.find(':')])
  return hour

def get_min(time):
  colon = time.find(':')
  return int(time[colon + 1: colon + 3])

def package_info(times, prices, carriers, start, end, hour, minute, isArriving, s):
  i = len(prices)
  dictionaries = []
  for j in range(len(prices)):
    if isArriving and (comp_times(times[2*j], hour, minute) and comp_times(times[2*j+1], hour, minute)):
      dictionaries.append(dict(price = prices[j], departure = start, arrival = end, departure_time = times[2 * j], arrival_time = times[2 * j+ 1], carrier = carriers[j], link = s, payload = ""))
    elif isArriving is False and (comp_times(times[2*j], hour, minute) is False):
        dictionaries.append(dict(price = prices[j], departure = start, arrival = end, departure_time = times[2 * j], arrival_time = times[2 * j+ 1], carrier = carriers[j], link = s, payload = ""))
  return dictionaries

def flights(start, end, month, day, year, hour, minute, isArriving, byPrice):
  s = ''
  if byPrice:
    s = 'http://www.orbitz.com/shop/home?type=air&ar.type=oneWay&ar.ow.leaveSlice.orig.dl=&ar.ow.leaveSlice.dest.dl=&ar.ow.leaveSlice.orig.key='+ str(start) + '&_ar.ow.leaveSlice.originRadius=0&ar.ow.leaveSlice.dest.key='+ str(end) + '&_ar.ow.leaveSlice.destinationRadius=0&ar.ow.leaveSlice.date='+ str(month) + '%2F' + str(day) + '%2F' + str(year) + '&ar.ow.leaveSlice.time=Anytime&ar.ow.numAdult=1&ar.ow.numSenior=0&ar.ow.numChild=0&ar.ow.child%5B0%5D=&ar.ow.child%5B1%5D=&ar.ow.child%5B2%5D=&ar.ow.child%5B3%5D=&ar.ow.child%5B4%5D=&ar.ow.child%5B5%5D=&ar.ow.child%5B6%5D=&ar.ow.child%5B7%5D=&_ar.ow.nonStop=0&_ar.ow.narrowSel=0&ar.ow.narrow=airlines&ar.ow.carriers%5B0%5D=&ar.ow.carriers%5B1%5D=&ar.ow.carriers%5B2%5D=&ar.ow.cabin=C&search=Search+Flights'
  else:
    s = 'http://www.orbitz.com/shop/home?type=air&ar.type=oneWay&ar.ow.leaveSlice.orig.dl=&ar.ow.leaveSlice.dest.dl=&ar.ow.leaveSlice.orig.key='+ str(start) + '&_ar.ow.leaveSlice.originRadius=0&ar.ow.leaveSlice.dest.key='+ str(end) + '&_ar.ow.leaveSlice.destinationRadius=0&ar.ow.leaveSlice.date='+ str(month) + '%2F' + str(day) + '%2F' + str(year) + '&ar.ow.leaveSlice.time=Anytime&ar.ow.numAdult=1&ar.ow.numSenior=0&ar.ow.numChild=0&ar.ow.child%5B0%5D=&ar.ow.child%5B1%5D=&ar.ow.child%5B2%5D=&ar.ow.child%5B3%5D=&ar.ow.child%5B4%5D=&ar.ow.child%5B5%5D=&ar.ow.child%5B6%5D=&ar.ow.child%5B7%5D=&_ar.ow.nonStop=0&_ar.ow.narrowSel=0&ar.ow.narrow=airlines&ar.ow.carriers%5B0%5D=&ar.ow.carriers%5B1%5D=&ar.ow.carriers%5B2%5D=&ar.ow.cabin=C&search=Search+Flights&view.sortType=AIR_JOURNEY_DURATION'
  html = urllib2.urlopen(s).read()
  times = re.findall("[0-9]*[0-9]:[0-9][0-9].*[AP]M </span>", html)
  times_s = sanitize_times(times)

  prices = re.findall("money-symbol.*\.[0-9][0-9]", html)
  prices_s = sanitize_prices(prices)

  carriers = re.findall(".* </strong>", html)
  carriers_s = sanitize_carriers(carriers)

  p = package_info(times_s, prices_s, carriers_s, start, end, hour, minute, isArriving, s)
  #print p
  return p

def contains(list, check):
  for i in list:
    if i == check:
      return True
  return False

def orbitz(start, end, month, day, year, hour, minute, isArriving):

  pool = ThreadPool(processes = 2)
  result1 = pool.apply_async(flights, (start, end, month, day, year, hour, minute, isArriving, True))
  result2 = pool.apply_async(flights, (start, end, month, day, year, hour, minute, isArriving, False))

  first = result1.get()
  second = result2.get()
#  first = flights(start, end, month, day, year, hour, minute, isArriving, True)
#  second = flights(start, end, month, day, year, hour, minute, isArriving, False)
  #print first
  for s in second:
    if contains(first, s) is False:
      first.append(s)
  if True: return first

if __name__ == '__main__':
    print orbitz("EWR", "BOS", 5, 30, 2013, 18, 30, False)
