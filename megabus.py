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

def package_info(times, prices, departures):
	dictionaries = []
	for j in range(len(prices)):
		dictionaries.append(dict(price = prices[j], departure = departures[2 * j], arrival = departures[2 * j + 1], departure_time = times[2 * j], arrival_time = times[2 * j+ 1], carrier = "Megabus"))
	return dictionaries


def megabus(start, end, month, day, year):
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

	p = package_info(times_s, prices, departures_s)
	print p
	return p

megabus(302, 289, 4, 14, 2013)
