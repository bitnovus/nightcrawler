import mechanize, sys, string
from bs4 import BeautifulSoup

def  main():
	url = "http://www.coachusa.com/coachss-v2/index.asp?action=GetSetOriginState"
	request = mechanize.Request(url)
	forms = getForms(request)

	#for form in forms:
	#	print form.name
	#	for control in form.controls:
	#		print control.name

	route1 = forms[1]

	control1 = route1.find_control("originState")
	for state in control1.items:
		if "*" in str(state):
			continue
		print "origin: " + str(state)
		#route1["originState"] = [state.name]
		route1["originState"] = ["NJ"]

		forms = getForms(route1.click())
		route2 = forms[2]
		#print route2
		control2 = route2.find_control("originCity")
		for city in control2.items:
			if "*" in str(city):
				continue
			print "origin: " + str(city)
			#route2["originCity"] = [city.name]
			route2["originCity"] = ["Princeton"]
			#route2["originCity"] = ["East Windsor"]
			forms = getForms(route2.click())
			route3 = forms[3]
			control3 = route3.find_control("destinationState")
			for destState in control3.items:
				if "*" in str(destState):
					continue
				print "dest: " + str(destState)
				#route3["destinationState"] = [destState.name]
				route3["destinationState"] = ["NJ"]
				forms = getForms(route3.click())
				route4 = forms[4]
				control4 = route4.find_control("destinationCity")
				for destCity in control4.items:
					if "*" in str(destCity):
						continue
					print "dest: " + str(destCity)
					#route4["destinationCity"] = [destCity.name]
					route4["destinationCity"] = ["New Brunswick"]
					#route4["destinationCity"] = ["Monroe Township"]


					route4.set_all_readonly(False)
					route4["sitePageName"] = "/coachss-v2/index.asp"
					print route4["sitePageName"]
					html = getHTML(route4.click())
					soup = BeautifulSoup(html)
					print soup.prettify()

					#check if there are multiple routes
					if html.find("Select a schedule / version from the list below to continue") != -1:
						print "returning"
						return

					numOrigin = 0
					numDest = 0

					#find class=tableHilightHeader
					print "finding"
					start = soup.find_all(tableStart)[0]
					#print start.contents
					for child in start.children:
						#print child
						if str(type(child)).find("NavigableString") != -1:
							continue
						# replace with city
						if str(child).find("Princeton") != -1:
							numOrigin = int(child.get('colspan'))
						elif str(child).find("New Brunswick") != -1:
							numDest = int(child.get('colspan'))

					#
					days = []
					originTimes = []
					destTimes = []
					locations = []

					parent = start.parent
					# get locations
					for child in parent.contents[3].children:
						#print child
						if str(type(child)).find("NavigableString") != -1:
							continue
						for td in child.find_all("td"):
							for img in td.find_all("img"):
								loc = img.get('title')
								if loc != None:
									locations.append(loc)


					# iterate through rows

					found = False
					for child in parent.find_all("tr"):
						if child == parent.contents[3]:
							found = True
							continue
						if not found:
							continue
						#print child
						cells = child.find_all("td")
						if len(cells) >= 2 + numDest + numOrigin:
							if str(cells[1 + numOrigin].contents[0]).find("img") != -1:
								# days of week
								days.append(string.strip(cells[0].contents[0]))
								# origin times
								times = ()
								for i in range(1,numOrigin+1):
									if cells[i].contents[0] != u'\xa0':
										#print cells[i].contents[0]
										times = times, cells[i].contents[0]
									else:
										times = times, 0
								originTimes.append(times)
								# destination times
								times = ()
								for i in range(2+numOrigin,numOrigin+numDest+2):
									if cells[i].contents[0] != u'\xa0':
										#print cells[i].contents[0]
										times = times, cells[i].contents[0]
									else:
										times = times, 0
								destTimes.append(times)


					# get price page

					return



def getForms(request, pr=False):
	response = mechanize.urlopen(request)
	if pr:
		#print response.geturl()
		print response.read()
	forms = mechanize.ParseResponse(response, backwards_compat=False)
	response.close()
	return forms

def getHTML(request):
	response = mechanize.urlopen(request)
	html = response.read()
	response.close()
	return html

def tableStart(tag):
	return tag.has_key('class') and (tag.get('class')[0].find("tableHilightHeader") != -1)

main()
