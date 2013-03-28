#!/usr/bin/env python
# -*- coding: utf-8 -*-
# scrape megabus routes by select departure points one at a time and parsing
# AJAX updates to destinations select box 
# john@lawnjam.com

from bs4 import BeautifulSoup
import urllib, urllib2, cookielib

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-gb,en;q=0.8,en-us;q=0.5,gd;q=0.3',
    'Accept-Encoding': 'gzip,deflate',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}

req = urllib2.Request('http://us.megabus.com/default.aspx')
response = urllib2.urlopen(req)

megaSoup = BeautifulSoup(response.read())
viewstate = megaSoup.find(name='input', attrs={'name': '__VIEWSTATE'})['value']
eventvalidation = megaSoup.find(name='input', attrs={'name': '__EVENTVALIDATION'})['value']
options = megaSoup.find(name='select', attrs={'name': 'SearchAndBuy1$ddlLeavingFrom'}).findAll('option')
startLocations = {}
for o in options:
    startLocations[int(o['value'])] = o.find(text=True)
del startLocations[0] # 0 is "Select"

# set other form values
values = {
    'Welcome1_ScriptManager1_HiddenField': '',
    'Welcome1$ScriptManager1': 'SearchAndBuy1$upSearchAndBuy|SearchAndBuy1$ddlLeavingFrom',
    '__EVENTTARGET': 'SearchAndBuy1$ddlLeavingFrom',
    '__EVENTARGUMENT': '',
    'Welcome1$hdnBasketItemCount': '0',
    'Language1$ddlLanguage': 'en',
    'SearchAndBuy1$txtPassengers': '1',
    'SearchAndBuy1$txtConcessions': '0',
    'SearchAndBuy1$txtNUSExtra': '0',
    'SearchAndBuy1$txtOutboundDate': '',
    'SearchAndBuy1$txtReturnDate': '',
    'SearchAndBuy1$txtPromotionalCode': '',
    '__ASYNCPOST': 'true'
    }
headers['X-MicrosoftAjax'] = 'Delta=true'

for a in startLocations:
    values['SearchAndBuy1$ddlLeavingFrom'] = a
    values['__EVENTVALIDATION'] = eventvalidation
    values['__VIEWSTATE'] = viewstate
    data = urllib.urlencode(values)
    req = urllib2.Request('http://us.megabus.com/default.aspx', data, headers)

    # store the received (pipe-separated) data in a list
    L = urllib2.urlopen(req).read().split('|')
    for position, item in enumerate(L):
        if item == 'SearchAndBuy1_upSearchAndBuy':
            html = L[position + 1]
        if item == '__VIEWSTATE':
            viewstate = L[position + 1] # save __VIEWSTATE for the next iteration
        if item == '__EVENTVALIDATION':
            eventvalidation = L[position + 1] # save __EVENTVALIDATION for the next iteration

    megaSoup = BeautifulSoup(html)
    options = megaSoup.find(name='select', attrs={'name': 'SearchAndBuy1$ddlTravelingTo'}).findAll('option')
    endLocations = {}
    for o in options:
        if int(o['value']) > 0:
            print '"' + startLocations[a] + '","' + o.find(text=True) + '"'
            #endLocations[int(o['value'])] = o.find(text=True)
    #print endLocations

"""
#print endLocations

# 2nd POST: set travelling to
values['__EVENTVALIDATION'] = eventvalidation
values['__VIEWSTATE'] = viewstate
values['Welcome1$ScriptManager1'] = 'SearchAndBuy1$upSearchAndBuy|SearchAndBuy1$ddlTravellingTo'
values['__EVENTTARGET'] = 'SearchAndBuy1$ddlTravellingTo'
values['__LASTFOCUS'] = ''
values['SearchAndBuy1$ddlTravellingTo'] = '10' # 10 is Birmingham
data = urllib.urlencode(values)req = urllib2.Request('http://uk.megabus.com/default.aspx', data, headers)

# store the received (pipe-separated) data in a list
L = urllib2.urlopen(req).read().split('|')

for position, item in enumerate(L):
    if item == '__VIEWSTATE':
        viewstate = L[position + 1]
    if item == '__EVENTVALIDATION':
        eventvalidation = L[position + 1]

# 3rd POST: set date
values['__EVENTVALIDATION'] = eventvalidation
values['__VIEWSTATE'] = viewstate
values['Welcome1$ScriptManager1'] = 'SearchAndBuy1$upSearchAndBuy|SearchAndBuy1$calendarOutboundDate'
values['__EVENTTARGET'] = 'SearchAndBuy1$calendarOutboundDate'
values['__EVENTARGUMENT'] = '4087' ###### FIXME map these values to actual dates - 4087 is 11/03/2011
values['SearchAndBuy1$ddlTravellingBy'] = '0'
data = urllib.urlencode(values)
req = urllib2.Request('http://uk.megabus.com/default.aspx', data, headers)
urllib2.urlopen(req)

# GET the results
req = urllib2.Request('http://uk.megabus.com/JourneyResults.aspx', None, headers)
print urllib2.urlopen(req).read()
"""
