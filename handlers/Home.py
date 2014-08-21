from google.appengine.ext import db
from Handler import Handler, check_login
from database import *
import time

class Home(Handler):
	@check_login
	def get(self):
		self.deleteOldRides()
		time.sleep(.25)

		#Rides
		userId = self.getUser()
		user = User.get_by_id(userId)
		rides = user.rides

		#note: sort this later
		for ride in rides:
			driver = ride.driver
			ride.driverName = driver.username
			ride.driverEmail = driver.email
				
		#Requests
		requests = list(user.requests_passenger)
		self.render("home.html", rides=rides, requests=requests)

	#This is for if they are cancelling a ride
	def post(self):
		rideId = int(self.request.get("rideId"))
		ride = Ride.get_by_id(rideId)
		ride.delete()
		time.sleep(.25)
		self.redirect('home')
