from google.appengine.ext import db
from Handler import Handler, check_login
from database import User, Ride
from pygeocoder import Geocoder

class View(Handler):
	def render_front(self, rides, start="", destination="", error=""):
		self.render("rideSearch.html", start=start, destination=destination, error=error)

	@check_login
	def get(self):
		#Initialization
		self.deleteOldRides()

		#Get current user
		userId = self.getUser()
		user = User.get_by_id(userId)

		#Finding the rides user is not in
		rideIds = user.rideIds
		rides = list(Ride.gql("ORDER BY startTime DESC LIMIT 10"))
		rides = [r for r in rides if r.key().id() not in rideIds]

		#Update ride information
		for ride in rides:
			ride.driverName = ride.driver.username
			ride.seatsLeft = ride.passengerMax - len(ride.passIds)

		#Finds the requests the user has made
		# requests = list(db.GqlQuery("SELECT * FROM Request WHERE requesterId = :userId", userId=self.getUser()))
		# requests = [x.rideId for x in requests]
		# rides = [x for x in rides if x.key().id() not in requests]
		# for ride in rides:
			# ride.driverName = User.get_by_id(ride.driverId).username

		sortType = self.request.get('sort', default_value='time')
		raw_start = self.request.get('start')
		raw_destination = self.request.get('dest')
		if sortType == 'time':
			rides = sorted(rides, key=lambda x:x.startTime)
		elif sortType == 'cost':
			rides = sorted(rides, key=lambda x:x.cost)
		elif sortType == 'start':
			try:
				start = Geocoder.geocode(raw_start)
			except:
				error = 'We could not find your start location. Please check that you spelled it correctly.'
				self.render_front(rides, rawStart, rawDestination, error)
				return
			rides = sorted(rides,
					key=lambda x:self.getLocationInfo(start, Geocoder.geocode(x.start))['distance']['value'])
		elif sortType == 'dest':
			try:
				destination = Geocoder.geocode(raw_destination)
			except:
				error = 'We could not find your destination. Please check that you spelled it correctly.'
				self.render_front(rides, rawStart, rawDestination, error)
				return
			rides = sorted(rides,
					key=lambda x: self.getLocationInfo(Geocoder.geocode(x.destination), destination)['distance']['value'])
		elif sortType == 'start_and_dest':
			try:
				start = Geocoder.geocode(raw_start)
			except:
				error = 'We could not find your start location. Please check that you spelled it correctly.'
				self.render_front(rides, rawStart, rawDestination, error)
				return
			try:
				destination = Geocoder.geocode(raw_destination)
			except:
				error = 'We could not find your destination. Please check that you spelled it correctly.'
				self.render_front(rides, rawStart, rawDestination, error)
				return
			total_distance = lambda x: self.getLocationInfo(start, Geocoder.geocode(x.start))['distance']['value'] + self.getLocationInfo(Geocoder.geocode(x.destination), destination)['distance']['value']

			rides = sorted(rides,
					key=total_distance)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		process = self.request.get('process')
		if process == 'more_info':
			self.redirect('/ride/'+self.request.get('rideId'))
		elif process == 'sort':
			self.redirect('/view?sort='+self.request.get('searchOptions')
					+ '&start=' + self.request.get('start')
					+ '&dest=' + self.request.get('dest'))
