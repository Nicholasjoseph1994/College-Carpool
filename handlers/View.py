from google.appengine.ext import db
from Handler import Handler
from database import User
from pygeocoder import Geocoder

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

		sortType = self.request.get('sort', default_value='time')
		if sortType == 'time':
			rides = sorted(rides, key=lambda x:x.startTime)
		elif sortType == 'cost':
			rides = sorted(rides, key=lambda x:x.cost)
		elif sortType == 'start':
			startLocation = Geocoder.geocode(self.request.get('start'))
			rides = sorted(rides,
					key=lambda x:self.getLocationInfo(startLocation, Geocoder.geocode(x.start))['distance']['value'])
		elif sortType == 'dest':
			destLocation = Geocoder.geocode(self.request.get('dest'))
			rides = sorted(rides,
					key=lambda x: self.getLocationInfo(Geocoder.geocode(x), destLocation)['distance']['value'])
		elif sortType == 'start_and_dest':
			startLocation = Geocoder.geocode(self.request.get('start'))
			destLocation = Geocoder.geocode(self.request.get('dest'))
			rides = sorted(rides,
					key=lambda x: self.getLocationInfo(startLocation, Geocoder.geocode(x.start))['distance']['value'] +
					self.getLocationInfo(Geocoder.geocode(x), destLocation)['distance']['value'])
		self.render("rideSearch.html", rides=rides)
	def post(self):
		process = self.request.get('process')
		if process == 'more_info':
			self.redirect('/'+self.request.get('rideId'))
		elif process == 'sort':
			#keep working here redirect to get request.
			self.redirect('/view?sort='+self.request.get('searchOptions')
					+ '&start=' + self.request.get('start')
					+ '&dest=' + self.request.get('dest'))
