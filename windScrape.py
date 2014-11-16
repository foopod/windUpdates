#!/usr/bin/env python

import mechanize
from datetime import datetime
import time
import re
from lxml import html
from collections import deque
from time import sleep
import emailyo

topSpeed = 0.0
fmt = '%H:%M:%S'
queue = deque()
emailRecipients=['sample@example.com']

#config.txt holds the topspeed of all time
with open("config.txt", "r") as myfile:
	s = myfile.read()
	topSpeed = float(s)

def getVelocity():
	# Browser
	br = mechanize.Browser()

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	# User-Agent (this is cheating, ok?)
	br.addheaders = [('User-agent', 'Android / Firefox 29: Mozilla/5.0 (Android; Mobile; rv:29.0) Gecko/29.0 Firefox/29.0')]

	#Open webpage, wifi was super spotty, so it retries forever
	r = None
	while r is None:
		try:
			r = br.open('https://example.com/')
		except:
			sleep(2)
			pass
	webpage = html.fromstring(r.read())

	#Querying the webpage using XPath
	s = webpage.xpath('//*[contains(text(), "initialWindSpeed")]/text()')[0]

	#Extracting values from the string
	m = re.search('var initialWindSpeed=(.+?);var in', s)
	speed = m.group(1)
	m = re.search('initialWindDirection=(.+?);var gameU', s)
	direction = m.group(1)

	return speed + ',' + direction

'''
	datetime_from_utc_to_local
	returns the local time converted from utc
'''
def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

'''
	stringness
	returns number as a string of 3 characters for pretty printing
'''
def stringness(number):
	string = str(number)
	if len(string) == 3:
		return ' ' + string
	else:
		return string

'''
	mainLoop
'''
while(True):
	#Get new speed/direction
	velocity = getVelocity()
	s = float(velocity.split(',')[0])
	d = float(velocity.split(',')[1])

	# if new topspeed then write to config file
	if (s > topSpeed):
		topSpeed = s
		print topSpeed
		with open("config.txt", "w") as myfile:
			myfile.write(str(topSpeed))
			print topSpeed

		message = 'Wind Speed : ' + str(s) + ' kts'
		emailyo.send_email(message, emailRecipients)

	#New speed goes on our list of 5 last speeds recorded
	if len(queue) == 5:
		queue.pop()
	queue.appendleft(s)

	#print the pretty table
	print chr(27) + "[2J"
	print '         ' + stringness(s) + ' kts        '+str(d) + u"\u00b0"
	print ' -------------------------------------- '
	print '|  Top Speed :             ' + stringness(topSpeed) + ' kts    |'
	print '|--------------------------------------|'
	first = True
	for q in queue:
		if first:
			print '|  Last Five :             ' + stringness(q) + ' kts    |'
			first = False
		else:
			print '|                          ' + stringness(q) + ' kts    |'
	print ' -------------------------------------- '
	print '                '+datetime_from_utc_to_local(datetime.utcnow()).strftime(fmt)
	print ''

	#update interval
	sleep(30)