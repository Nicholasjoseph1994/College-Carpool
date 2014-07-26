from google.appengine.ext import db
from Handler import Handler
from database import *
class RidePage(Handler):
	def get(self, rideId):
		self.checkLogin()
		ride = Ride.get_by_id(int(rideId))
		ride.driverName = User.get_by_id(ride.driverId).username
		self.render("ride.html", ride=ride)
	def post(self, rideId):
		request = Request(driverId=int(self.request.get('driverId')), rideId=int(self.request.get('rideId')), requesterId=self.getUser(), message=self.request.get('message'))
		request.put()
		time.sleep(.5)
		self.redirect("/home")
