
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
			ride.driverName = ride.driver.username
			ride.seatsLeft = ride.passengerMax - len(ride.passIds)
			
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/'+self.request.get('rideId'))
