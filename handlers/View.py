
from google.appengine.ext import db
from Handler import Handler
from database import User, Ride, Request

class View(Handler):
	def get(self):
		#Initialization
		self.deleteOldRides()
		self.checkLogin()

		#Finding the rides user is not in
		rides = list(Ride.gql("ORDER BY startTime DESC LIMIT 10"))
		notInRide = lambda x: x.driver.key().id() != self.getUser() and str(self.getUser()) not in x.passIds
		rides = filter(notInRide, rides)

		#Finds the requests the user has made
		requests = list(Request.gql("WHERE requesterId = :userId", userId=self.getUser()))
		requests = [x.rideId for x in requests]
		rides = [x for x in rides if x.key().id() not in requests]
		for ride in rides:
			ride.driverName = ride.driver.username
			
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/'+self.request.get('rideId'))
