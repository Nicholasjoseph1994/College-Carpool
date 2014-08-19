from google.appengine.ext import db
#Table for Rides 
class Ride(db.Model):
	start = db.StringProperty(required = True)
	destination = db.StringProperty(required=True)
	startTime = db.DateTimeProperty(auto_now_add=True)
	driverId = db.IntegerProperty(required=True)
	passengerMax = db.IntegerProperty(required=True)
	cost = db.FloatProperty(required=True)
	driveTime = db.IntegerProperty(required=True)
	driveDistance = db.FloatProperty(required=True)
	passIds = db.StringProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
#Table for Users
class User(db.Model):
	username = db.StringProperty(required=True)
	passHash = db.TextProperty(required=True)
	email = db.StringProperty(required=True)
	venmo_email = db.StringProperty(required=False)
	bio = db.TextProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
	activationCode = db.StringProperty()
	activated = db.BooleanProperty(default=False)
#Table for requests
class Request(db.Model):
	driverId = db.IntegerProperty(required=True)
	rideId = db.IntegerProperty(required=True)
	requesterId = db.IntegerProperty(required=True)
	message = db.TextProperty(required=False)

	def put(self):
		super(Request, self).put()
		# add a PassengerRequestNotification to driverId
		requestNotification = PassengerRequestNotification(requestId=self.key().id(), driverId=self.driverId, type="passenger-request")
		requestNotification.put()

	def delete(self):
		PassengerRequestNotification.gql("WHERE requestId=%s" % (self.key().id())).get().delete()
		super(Request, self).delete()

#Table for requester->driver notifications
class PassengerRequestNotification(db.Model):
	requestId = db.IntegerProperty(required=True)
	driverId = db.IntegerProperty(required=True)
	type = db.StringProperty(required=True, choices=set(["passenger-request"]))

#Table for driver->requester notifications
class DriverResponseNotification(db.Model):
	rideId = db.IntegerProperty(required=True)
	requesterId = db.IntegerProperty(required=True)
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