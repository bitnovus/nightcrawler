import mechanize, sys

def  main():
	url = "http://www.coachusa.com/coachss-v2/index.asp?action=GetSetOriginState"
	request = mechanize.Request(url)
	forms = getForms(request)
	#response = mechanize.urlopen(request)
	#forms = mechanize.ParseResponse(response, backwards_compat=False)
	#response.close()

	#for form in forms:
	#	print form.name
	#	for control in form.controls:
	#		print control.name

	route1 = forms[1]

	control1 = route1.find_control("originState")
	for state in control1.items:
		if "*" in str(state):
			continue
		print state
		route1["originState"] = [state.name]

		forms = getForms(route1.click())
		route2 = forms[2]
		#print route2
		control2 = route2.find_control("originCity")
		for city in control2.items:
			if "*" in str(city):
				continue
			print city
			route2["originCity"] = [city.name]
			forms = getForms(route2.click())
			route3 = forms[3]
			control3 = route3.find_control("destinationState")
			for destState in control3.items:
				if "*" in str(destState):
					continue
				print destState
				route3["destinationState"] = [destState.name]
				forms = getForms(route3.click())
				route4 = forms[4]
				control4 = route4.find_control("destinationCity")

			
			


def getForms(request):
	response = mechanize.urlopen(request)
	#print response
	forms = mechanize.ParseResponse(response, backwards_compat=False)
	response.close()
	return forms

main()
