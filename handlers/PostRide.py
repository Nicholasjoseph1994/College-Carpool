from google.appengine.ext import db
from Handler import Handler
from database import *
import validation
import datetime
import time
import logging
import re
import string

class PostRide(Handler):
	#Renders the form
	def render_front(self, start="", destination="", startDate="", startTime="", cost="", passengerMax="", error=""):
		self.render("postRide.html", start=start, destination=destination, startDate=startDate, startTime=startTime, cost=cost, passengerMax=passengerMax, error=error)

	def get(self):
		self.checkLogin()
		self.render_front()

	#Posts a new ride for people to join
	def post(self):
		#Validates all of the input from the form
		def validate_inputs(start, destination, cost, passengerMax, dateInput, timeInput):
			MAXIMUM_SIZE = 8
			TIME_PATTERN = re.compile(r"^((0?[1-9])|(1[0-2])):[0-5]\d\s*([AP]M|[ap]m)$")
			res = True
			error = ""
			if not start:
				error = "Please enter a starting location."
				res =  False
			if not destination:
				error = "Please enter a destination."
				res = False
			if not cost or cost < 0:
				error = "Please enter a non-negative cost."
				res = False
			if not passengerMax or (passengerMax < 1) or (passengerMax > MAXIMUM_SIZE):
				error = "Please enter a number of passengers between 1 and " + str(MAXIMUM_SIZE)
				res = False
			try:
				date = datetime.datetime.strptime(dateInput, '%m/%d/%Y')
			except ValueError:
				error = "Please enter a valid date according to the format MM/DD/YYYY"
				res = False
			else:
				if date < datetime.datetime.now():
					error = "Please enter a future date."
					res = False
			if not TIME_PATTERN.match(timeInput):
				error = "Please enter the time according to the format HH:MM AM/PM"
				res = False
			if error:
				self.render_front(start, destination, dateInput, timeInput, cost, passengerMax, error)
			return res

		start = self.request.get("start")
		destination = self.request.get("destination")
		cost = self.request.get("cost")
		passengerMax = int(self.request.get("passengerMax"))
		dateInput = self.request.get("date")#The plain string input
		timeInput = self.request.get("time")#The plain string input
		driverId = self.getUser()

		if validate_inputs(start, destination, cost, passengerMax, dateInput, timeInput):
			date = map(int, dateInput.split("/", 2))
			timeFull = timeInput.split(" ")
			inputTime = map(int, timeFull[0].split(":"))

			#Checks AM/PM
			if "PM" in inputTime:
				inputTime[0] += 12

			startTime = datetime.datetime(date[2],date[0],date[1],inputTime[0],inputTime[1],0)
			if startTime < datetime.datetime.now():
				error = "You can't create past rides"
				self.render_front(start, destination, '', '', cost, passengerMax, error)
			else:
				ride = Ride(start=start, destination=destination, startTime=startTime, cost=float(cost), passengerMax=passengerMax, driverId=driverId, passIds="")
				ride.put()

				time.sleep(.25) #so that it has time to enter the ride and it appears on home page
				self.redirect("home")
