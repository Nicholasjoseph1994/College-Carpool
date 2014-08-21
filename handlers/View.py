
from Handler import Handler, check_login
from database import User, Ride

class View(Handler):
	@check_login
	def get(self):
		#Initialization
		self.deleteOldRides()
		
		userID = self.getUser()
		user = User.get_by_id(userID)

		#Finding the rides user is not in
		rides = list(Ride.gql("ORDER BY startTime DESC LIMIT 10"))
		notInRide = lambda x: x.driver.key().id() != userID and str(userID) not in x.passIds
		rides = filter(notInRide, rides)

		#Finds the requests the user has made
		requests = user.requests_passenger
		requests = [x.ride.key().id() for x in requests]
		rides = filter(lambda x: x.key().id() not in requests, rides)
		
		for ride in rides:
			ride.driverName = ride.driver.username
			ride.seatsLeft = ride.passengerMax - len(ride.passIds)
			
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/'+self.request.get('rideId'))
