from google.appengine.ext import db
from Handler import Handler
from database import *
class Home(Handler):
	def render_front(self, rides, requests):
		self.render("home.html", rides=rides, requests=requests)
	def get(self):
		self.deleteOldRides()
		time.sleep(.25)
		self.checkLogin()
		if memcache.get('venmo_token'):
			data = {'name': memcache.get('venmo_username'),
					'consumer_id': CONSUMER_ID,
					'access_token': memcache.get('venmo_token'),
					'signed_into_venmo': True}
		else:
			data = {'signed_into_venmo': False,
					'consumer_id': CONSUMER_ID}

		#Rides
		rides = list(Ride.all())
		userId = self.getUser()
		#note: sort this later
		if len(rides)>0:
			rides = filter(lambda x: x.driverId == userId or (x.passIds and str(userId) in x.passIds), rides)
		for ride in rides:
			driver = User.get_by_id(ride.driverId)
			driverName = driver.username
			driverEmail = driver.email
			ride.driverName = driverName
			ride.driverEmail = driverEmail
			if ride.passIds:
				ride.passengers = map(User.get_by_id,map(int,ride.passIds.split(",")))
		#Requests
		requests = list(db.GqlQuery('SELECT * FROM Request WHERE requesterId=:userId', userId = userId))
		for request in requests:
			ride = Ride.get_by_id(request.rideId)
			ride.driverName = User.get_by_id(ride.driverId).username
			ride.driverEmail = User.get_by_id(ride.driverId).email
			request.ride = ride
		self.render_front(rides, requests)
	#This is for if they are cancelling a ride
	def post(self):
		rideId = int(self.request.get("rideId"))
		ride = Ride.get_by_id(rideId)
		ride.delete()
		time.sleep(.25)
		self.redirect('home')
