from google.appengine.ext import db
from Handler import Handler
from database import *
import time

class Home(Handler):
	def render_front(self, rides, requests):
		self.render("home.html", rides=rides, requests=requests)

	def get(self):
		self.deleteOldRides()
		time.sleep(.25)
		self.checkLogin()

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
		self.render_front(rides, requests)

	#This is for if they are cancelling a ride
	def post(self):
		rideId = int(self.request.get("rideId"))
		ride = Ride.get_by_id(rideId)
		ride.delete()
		time.sleep(.25)
		self.redirect('home')
