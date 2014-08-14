
from google.appengine.ext import db
from Handler import Handler
from database import User

class View(Handler):
	def get(self):
		#Initialization
		self.deleteOldRides()
		self.checkLogin()

		#Finding the rides user is not in
		rides = list(db.GqlQuery("SELECT * FROM Ride ORDER BY startTime DESC", userId=self.getUser()))
		notInRide = lambda x: x.driverId!=self.getUser() and str(self.getUser()) not in x.passIds
		rides = filter(notInRide, rides)

		#Finds the requests the user has made
		requests = list(db.GqlQuery("SELECT * FROM Request WHERE requesterId = :userId", userId=self.getUser()))
		requests = [x.rideId for x in requests]
		rides = [x for x in rides if x.key().id() not in requests]
		for ride in rides:
			ride.driverName = User.get_by_id(ride.driverId).username
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/'+self.request.get('rideId'))
