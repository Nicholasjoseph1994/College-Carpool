from Handler import Handler, check_login
from database import *
import datetime
import time
import re
from pygeocoder import Geocoder

class PostRide(Handler):
	#Renders the form
	def render_front(self, start="", destination="", startDate="", startTime="", cost="", passengerMax="", error=""):
		self.render("postRide.html", start=start, destination=destination, startDate=startDate, startTime=startTime, cost=cost, passengerMax=passengerMax, error=error)

	@check_login
	def get(self):
		self.render_front()

	#Posts a new ride for people to join
	def post(self):
		#Validates all of the input from the form
		def validate_inputs(start, destination, cost, passengerMax, dateInput, timeInput):
			MAXIMUM_SIZE = 8
			TIME_PATTERN = re.compile(r"^((0?[1-9])|(1[0-2])):[0-5]\d\s*([AP]M|[ap]m)$")
			res = True
			error = ''
			if not start:
				error = 'Please enter a starting location.'
				res =  False
			elif not destination:
				error = 'Please enter a destination.'
				res = False
			elif not cost or cost < 0:
				error = 'Please enter a non-negative cost.'
				res = False
			elif not passengerMax or (passengerMax < 1) or (passengerMax > MAXIMUM_SIZE):
				error = 'Please enter a number of passengers between 1 and ' + str(MAXIMUM_SIZE)
				res = False
			elif not TIME_PATTERN.match(timeInput):
				error = 'Please enter the time according to the format HH:MM AM/PM'
				res = False
			else:
				try:
					date = datetime.datetime.strptime(dateInput, '%m/%d/%Y')
				except ValueError:
					error = 'Please enter a valid date according to the format MM/DD/YYYY'
					res = False
				else:
					if date < datetime.datetime.now():
						error = 'Please enter a future date.'
						res = False
			if error:
				self.render_front(start, destination, dateInput,
						timeInput, cost, passengerMax, error)
			return res

		rawStart = self.request.get('start')
		rawDestination = self.request.get('destination')
		cost = self.request.get("cost")
		# Makes sure that passengerMax has something in it that can be an int
		try:
			passengerMax = int(self.request.get("passengerMax"))
		except ValueError:
			passengerMax = None
		dateInput = self.request.get("date")#The plain string input
		timeInput = self.request.get("time")#The plain string input
		driverId = self.getUser()

		failed = False
		start, destination = None, None
		try:
			start = Geocoder.geocode(rawStart)
		except:
			error = 'We could not find your start location. Please check that you spelled it correctly.'
			failed = True
		try:
			destination = Geocoder.geocode(rawDestination)
		except:
			error = 'We could not find your destination. Please check that you spelled it correctly.'
			failed = True
			
		if failed:
			self.render_front(rawStart, rawDestination, dateInput, timeInput, cost, passengerMax, error)
			return
			
		if validate_inputs(rawStart, rawDestination, cost, passengerMax, dateInput, timeInput):
			#Procceses date/time input
			date = map(int, dateInput.split("/", 2))
			timeFull = timeInput.split(" ")
			inputTime = map(int, timeFull[0].split(":"))

			#Checks AM/PM
			if "PM" in inputTime:
				inputTime[0] += 12

			startTime = datetime.datetime(date[2],date[0],date[1],inputTime[0],inputTime[1],0)

			#Get distance and time infomration
			locationInfo = self.getLocationInfo(start, destination)
			rideDuration = locationInfo['duration']['value']
			rideDistance = locationInfo['distance']['value']

			#Check that the ride is in the present
			if startTime < datetime.datetime.now():
				error = "You can't create past rides"
				self.render_front(start.formatted_address, destination.formatted_address,
						'', '', cost, passengerMax, error)
			else:
				driver = User.get_by_id(driverId)
				
				ride = Ride(start=start.formatted_address,
						destination=destination.formatted_address,
						startTime=startTime,
						cost=float(cost),
						passengerMax=passengerMax,
						driver=driver,
						driveTime=float(rideDuration),
						driveDistance=float(rideDistance))
				ride.put()
				
				driver.addRide(ride)
				driver.put()
				
				time.sleep(.25) #so that it has time to enter the ride and it appears on home page
				self.redirect("home")
