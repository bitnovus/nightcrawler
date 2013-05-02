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

# returns true if time is before hour and minute
# hours are between 0 and 23 when they are passed in 
def comp_times(time, hour, min):
  hour2 = int(get_hour(time))
  if time[time.find(':') + 4]=='P' and hour2!=12:
    hour2 = hour2 + 12
  if time[time.find(':') + 4]=='A' and hour2==12:
    hour2 = hour2 - 12
  min2 = int(get_min(time))
  if (hour2<hour) or (hour2==hour and min2<min):
    return True
  else: return False

def get_hour(time):
  hour = int(time[0:time.find(':')])
  return hour

def get_min(time):
  colon = time.find(':')
  return int(time[colon + 1: colon + 3])

def package_info(times, prices, departures, hour, minute, isArriving, s):
  dictionaries = []
  for j in range(len(prices)):
    # we need both arrival and departure times to be before the given time
    if isArriving and (comp_times(times[2*j], hour, minute) and comp_times(times[2*j+1], hour, minute)):
      dictionaries.append(dict(price = prices[j], departure = departures[2*j], arrival = departures[2*j+1], departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "Megabus", url = s))
    elif isArriving is False and (comp_times(times[2*j], hour, minute) is False):
      dictionaries.append(dict(price = prices[j], departure = departures[2*j], arrival = departures[2*j+1], departure_time = times[2*j], arrival_time = times[2*j+1], carrier = "Megabus", url=s))
  return dictionaries

def megabus(start, end, month, day, year, hour, minute, isArriving):
  link = "https://us.megabus.com/JourneyResults.aspx?originCode=" + str(start) + "&destinationCode=" + str(end) + "&outboundDepartureDate=" + str(month) + "%2f" + str(day) + "%2f" + str(year) + "&inboundDepartureDate=&passengerCount=1&transportType=0&concessionCount=0&nusCount=0&outboundWheelchairSeated=0&outboundOtherDisabilityCount=0&inboundWheelchairSeated=0&inboundOtherDisabilityCount=0&outboundPcaCount=0&inboundPcaCount=0&promotionCode=&withReturn=0"
  html = urllib2.urlopen(link).read()

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

  p = package_info(times_s, prices, departures_s, hour, minute, isArriving, link)
  #print p
  return p

if __name__ == '__main__':
    megabus(94, 123, 5, 27, 2013, 20, 30, False)
