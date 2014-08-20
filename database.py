from google.appengine.ext import db

#Table for Users
class User(db.Model):
	username = db.StringProperty(required=True)
	passHash = db.TextProperty(required=True)
	email = db.StringProperty(required=True)
	venmo_email = db.StringProperty(required=False)
	venmoID = db.IntegerProperty(required=False)
	bio = db.TextProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
	activationCode = db.StringProperty()
	activated = db.BooleanProperty(default=False)
	recoveryCode = db.StringProperty()
	
	rideIds = db.ListProperty(int)
	
	def addRide(self, ride):
		self.rideIds.append(ride.key().id())
		
	def getRides(self):
		return [Ride.get_by_id(ride) for ride in self.rideIds]

#Table for Rides 
class Ride(db.Model):
	start = db.StringProperty(required = True)
	destination = db.StringProperty(required=True)
	startTime = db.DateTimeProperty(auto_now_add=True)
	driver = db.ReferenceProperty(User, required=True)
	passengerMax = db.IntegerProperty(required=True)
	cost = db.FloatProperty(required=True)
	driveTime = db.FloatProperty(required=True)
	driveDistance = db.FloatProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	
	passIds = db.ListProperty(int)
	
	def addRide(self, passenger):
		self.passIds.append(passenger.key().id())
		
	def getRides(self):
		return [User.get_by_id(passenger) for passenger in self.passIds]

#Table for requests
class Request(db.Model):
	driver = db.ReferenceProperty(User, required=True, collection_name="requests_driver")
	ride = db.ReferenceProperty(Ride, required=True, collection_name="ride_requests")
	passenger = db.ReferenceProperty(User, required=True, collection_name="requests_passenger")
	
	message = db.TextProperty(required=False)

	def put(self):
		super(Request, self).put()
		# add a PassengerRequestNotification to driverId
		requestNotification = PassengerRequestNotification(request=self, driver=self.driver, type="passenger-request")
		requestNotification.put()

	def delete(self):
		for request in self.requests:
			request.delete()
# 		PassengerRequestNotification.gql("WHERE requestId=%s" % (self.key().id())).get().delete()
		super(Request, self).delete()

#Table for requester->driver notifications
class PassengerRequestNotification(db.Model):
	request = db.ReferenceProperty(Request, required=True, collection_name="requests")
	driver = db.ReferenceProperty(User, required=True, collection_name="passenger_requests")
	type = db.StringProperty(required=True, choices=set(["passenger-request"]))

#Table for driver->requester notifications
class DriverResponseNotification(db.Model):
	ride = db.ReferenceProperty(Ride, required=True, collection_name="driver_responses")
	passenger = db.ReferenceProperty(User, required=True, collection_name="driver_responses")
	type = db.StringProperty(required=True, choices=set(["accepted-ride","rejected-ride"]))

# Table for payment statuses
class Payment(db.Model):
	type = db.StringProperty(required=True, choices=set(["Venmo"]))
	dateCreated = db.DateTimeProperty(required=True)
	status = db.StringProperty(required=True)
	payerID = db.IntegerProperty(required=True) # api ID (i.e. venmo ID)
	receiverID = db.IntegerProperty(required=True) # api ID (i.e. venmo ID)
	apiID = db.StringProperty(required=True)
	amount = db.FloatProperty(required=True)
	note = db.StringProperty()
	lastUpdate = db.DateTimeProperty()