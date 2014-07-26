from google.appengine.ext import db
from Handler import Handler
from database import *
import validation
import datetime
import time

class PostRide(Handler):
	def render_front(self, start="", destination="", startDate="", startTime="", cost="", passengerMax="", error=""):
		self.render("postRide.html", start=start, destination=destination, startDate=startDate, startTime=startTime, cost=cost, passengerMax=passengerMax, error=error)
	def get(self):
		self.checkLogin()
		self.render_front()
	#This method needs to be reordered so that it checks for all of the fields being full first thing
	def post(self):
		start = self.request.get("start")
		destination = self.request.get("destination")
		cost = self.request.get("cost")
		passengerMax = self.request.get("passengerMax")
		dateInput = self.request.get("date")#The plain string input
		timeInput = self.request.get("time")#The plain string input
		driverId = self.request.cookies.get('user')
		if driverId:
			driverId = validation.check_secure_val(driverId)
			if driverId:
				driverId = int(driverId)
		#date time stuff
		if start and destination and cost and passengerMax and dateInput and timeInput:
			date = map(int, dateInput.split("/",2))
			timeFull = timeInput.split(" ")
			inputTime = map(int, timeFull[0].split(":"))

			if "PM" in inputTime:
				inputTime[0] += 12

			startTime = datetime.datetime(date[2],date[0],date[1],inputTime[0],inputTime[1],0)
			if startTime < datetime.datetime.now():
				error = "You can't create past rides"
				self.render_front(start, destination, '', '', cost, passengerMax, error)
			else:
				ride = Ride(start=start, destination=destination, startTime=startTime, cost=float(cost), passengerMax=int(passengerMax), driverId=driverId, passIds="")
				ride.put()

				time.sleep(.25) #so that it has time to enter the ride and it appears on home page
				self.redirect("home")
		else:
			error = "Please fill out all the fields!"
			self.render_front(start, destination, dateInput, timeInput, cost, passengerMax, error)
