from google.appengine.ext import db
from Handler import Handler
from database import User
from pygeocoder import Geocoder
from Handler import Handler, check_login
from database import User, Ride

class View(Handler):
	@check_login
	def get(self):
		self.deleteOldRides()

		userID = self.getUser()
		user = User.get_by_id(userID)

		rideIds = user.rideIds
		#Finding the rides user is not in
		rides = list(Ride.gql("ORDER BY startTime DESC LIMIT 10"))
		rides = [r for r in rides if r.key().id() not in rideIds]

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
			ride.driverName = ride.driver.username
			ride.seatsLeft = ride.passengerMax - len(ride.passIds)
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/ride/'+self.request.get('rideId'))
