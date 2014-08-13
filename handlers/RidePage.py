from google.appengine.ext import db
from google.appengine.api import channel
from Handler import Handler
from database import *
import time

class RidePage(Handler):
	def get(self, rideId):
		self.checkLogin()
		ride = Ride.get_by_id(int(rideId))
		ride.driverName = User.get_by_id(ride.driverId).username
		self.render("ride.html", ride=ride)
	def post(self, rideId):
		driverId=int(self.request.get('driverId'))
		request = Request(driverId=driverId, rideId=int(self.request.get('rideId')), requesterId=self.getUser(), message=self.request.get('message'))
		request.put()
		#print "Sending message to " + str(driverId)
		channel.send_message(str(driverId), "{}");
		time.sleep(.5)
		self.redirect("/home")
