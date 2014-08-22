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
	activationCode = db.StringProperty(required=True)
	activated = db.BooleanProperty(default=False)
	recoveryCode = db.StringProperty()
	
	rideIds = db.ListProperty(int)
	
	def addRide(self, ride):
		self.rideIds.append(ride.key().id())
		
	def removeRide(self, ride):
		rideID = ride.key().id()
		self.rideIds = [r for r in self.rideIds if r != rideID]
		
	@property
	def rides(self):
		return [Ride.get_by_id(ride) for ride in self.rideIds]
	
	def archive(self):
		archive_entity(self, User_ARCHIVE)

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
	
	def addPassenger(self, passenger):
		self.passIds.append(passenger.key().id())
	
	def removePassenger(self, passenger):
		passID = passenger.key().id()
		self.passIds = [p for p in self.passIds if p != passID]
	
	@property
	def passengers(self):
		return [User.get_by_id(passenger) for passenger in self.passIds]
	
	def archive(self):
		archive_entity(self, Ride_ARCHIVE)

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
		for request in self.passenger_requests:
			request.delete()
# 		PassengerRequestNotification.gql("WHERE requestId=%s" % (self.key().id())).get().delete()

		super(Request, self).delete()
		
	def archive(self):
		archive_entity(self, Request_ARCHIVE)

#Table for requester->driver notifications
class PassengerRequestNotification(db.Model):
	request = db.ReferenceProperty(Request, required=True, collection_name="passenger_requests")
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
	
	driver = db.ReferenceProperty(User, required=True, collection_name="incoming_payments")
	passenger = db.ReferenceProperty(User, required=True, collection_name="outgoing_payments")
	
	apiID = db.StringProperty(required=True)
	amount = db.FloatProperty(required=True)
	note = db.StringProperty()
	lastUpdate = db.DateTimeProperty()

# archive models (should be clones of actual models)
# perhaps, need to look at references
# modify delete in models so that in actual model: modify references
# 								  in archive: delete references

#Table for Rides 
class User_ARCHIVE(db.Model):
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

class Ride_ARCHIVE(db.Model):
	start = db.StringProperty(required = True)
	destination = db.StringProperty(required=True)
	driver = db.StringProperty(required=True)
	startTime = db.DateTimeProperty(auto_now_add=True)
	passengerMax = db.IntegerProperty(required=True)
	cost = db.FloatProperty(required=True)
	driveTime = db.FloatProperty(required=True)
	driveDistance = db.FloatProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

class Request_ARCHIVE(db.Model):
	driver = db.StringProperty(required=True)
	ride = db.StringProperty(required=True)
	passenger = db.StringProperty(required=True)
	
	message = db.TextProperty(required=False)

# Archiving functions
def archive_entity(e, to_model, **extra_args):
	archived = clone_entity(e, to_model, **extra_args)
	archived.put()
	
	e.delete()

def clone_entity(e, to_klass, **extra_args):
	"""Clones an entity, adding or overriding constructor attributes.

  The cloned entity will have exactly the same property values as the original
  entity, except where overridden. By default it will have no parent entity or
  key name, unless supplied.

  Args:
    e: The entity to clone
    extra_args: Keyword arguments to override from the cloned entity and pass
      to the constructor.
  Returns:
    A cloned, possibly modified, copy of entity e.
    """
	klass = e.__class__
		
	props = dict() 

	for k, v in klass.properties().iteritems():
		if isinstance(v, db.ReferenceProperty):
			# copy reference property key as StringProperty
			key = getattr(klass, k).get_value_for_datastore(e)
			props[k] = str(key)
		else:
			props[k] = v.__get__(e, klass)
			
	props.update(extra_args)
	return to_klass(**props)
