
from google.appengine.ext import db
from Handler import Handler
from database import User, Ride, Request

class View(Handler):
	def get(self):
		#Initialization
		self.deleteOldRides()
		self.checkLogin()
		
		userID = self.getUser()
		user = User.get_by_id(userID)

		#Finding the rides user is not in
		rides = list(Ride.gql("ORDER BY startTime DESC LIMIT 10"))
		notInRide = lambda x: x.driver.key().id() != userID and str(userID) not in x.passIds
		rides = filter(notInRide, rides)

		#Finds the requests the user has made
		requests = user.requests_passenger
		requests = [x.ride for x in requests]
		rides = filter(lambda x: x not in requests, rides)
		
		for ride in rides:
			ride.driverName = ride.driver.username
			
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/'+self.request.get('rideId'))
