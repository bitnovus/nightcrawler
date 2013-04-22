#!/bin/env python

import urllib2, re

def sanitize_times(times):
  g = []
  for t in times:
    g.append(re.sub(r"\xc2\xa0", " ", t))
  return g

def sanitize_departures(departures):
  g = []
  for d in departures:
    s = re.sub(r"ALBACORE\t\t\t\t\t\t\t\t", "", d)
    s = re.sub("\rAARDVARK", "", s)
    g.append(s)
  return g

def get_hour(time):
  hour = int(time[0:time.find(':')])
  if time[time.find(':') + 4] == 'P' or hour==12 or hour==1:
    hour = hour + 12
  return hour

def get_min(time):
  colon = time.find(':')
  return int(time[colon + 1: colon + 3])

def package_info(times, prices, departures, hour, minute, isArriving):
  dictionaries = []
  for j in range(len(prices)):
    if isArriving and (get_hour(times[2*j+1]) < hour or (get_hour(times[2*j+1]) == hour and get_min(times[2*j+1]) <= minute)):
      dictionaries.append(dict(price = prices[j], departure = departures[2*j], arrival = departures[2*j+1], departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "Megabus"))
    elif isArriving is False and (get_hour(times[2*j]) > hour or (get_hour(times[2*j]) == hour and get_min(times[2*j]) >= minute)):
      dictionaries.append(dict(price = prices[j], departure = departures[2*j], arrival = departures[2*j+1], departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "Megabus"))
  return dictionaries

def megabus(start, end, month, day, year, hour, minute, isArriving):
  s = "https://us.megabus.com/JourneyResults.aspx?originCode=" + str(start) + "&destinationCode=" + str(end) + "&outboundDepartureDate=" + str(month) + "%2f" + str(day) + "%2f" + str(year) + "&inboundDepartureDate=&passengerCount=1&transportType=0&concessionCount=0&nusCount=0&outboundWheelchairSeated=0&outboundOtherDisabilityCount=0&inboundWheelchairSeated=0&inboundOtherDisabilityCount=0&outboundPcaCount=0&inboundPcaCount=0&promotionCode=&withReturn=0"
  html = urllib2.urlopen(s).read()

  times = re.findall("[0-9]*[0-9]:[0-9][0-9].*[AP]M", html)
  times_s = sanitize_times(times)

  prices = re.findall("\$[0-9]*\.[0-9][0-9]", html)
  lines = html.split("\n")
  s = ""
  next = False
  for line in lines:
    if next:
      s = s + "ALBACORE" + line + "AARDVARK \n"
      next = False
    else:
      s = s + line + " "
    if ",<!-- mp_trans -->" in line:
      next = True

  departures = re.findall("ALBACORE.*AARDVARK", s)
  departures_s = sanitize_departures(departures)

  p = package_info(times_s, prices, departures_s, hour, minute, isArriving)
  #print p
  return p

if __name__ == '__main__':
    megabus(89, 123, 4, 25, 2013, 13, 30, False)
