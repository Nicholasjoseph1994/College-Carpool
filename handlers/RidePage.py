from google.appengine.ext import db
from google.appengine.api import channel
from Handler import Handler, check_login
from database import *
import time

class RidePage(Handler):
	@check_login
	def get(self, rideId):
		ride = Ride.get_by_id(int(rideId))
		ride.driverName = ride.driver.username
		ride.seatsLeft = ride.passengerMax - len(ride.passIds)
		
		self.render("ride.html", ride=ride)
		
	def post(self, rideId):
		driverId=int(self.request.get('driverId'))
		passenger = User.get_by_id(self.getUser())
		ride=Ride.get_by_id(int(rideId))
		
		if passenger.permission == "guest":
			ride.driverName = ride.driver.username
			ride.seatsLeft = ride.passengerMax - len(ride.passIds)
			self.render("ride.html", ride=ride, error="Permission Denied")
			return
		
		request = Request(driver=User.get_by_id(driverId), 
						ride=ride, 
						passenger=passenger, 
						message=self.request.get('message'))
		request.put()
		
		print "Sending message to " + str(driverId)
		channel.send_message(str(driverId), "{}");
# 		time.sleep(.5)
		self.redirect("/home")
