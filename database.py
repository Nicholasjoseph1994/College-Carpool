from google.appengine.ext import db
from google.appengine.ext import ndb
import time
import webapp2_extras.appengine.auth.models
from webapp2_extras import security

#Table for Rides 
class Ride(db.Model):
	start = db.StringProperty(required = True)
	destination = db.TextProperty(required=True)
	startTime = db.DateTimeProperty(auto_now_add=True)
	driverId = db.IntegerProperty(required=True)
	passengerMax = db.IntegerProperty(required=True)
	cost = db.FloatProperty(required=True)
	passIds = db.StringProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
#Table for Users
class User(webapp2_extras.appengine.auth.models.User):
	def set_password(self, raw_password):
		"""Sets the password for the current user

		:param raw_password:
			The raw password which will be hashed and stored
		"""
		self.password = security.generate_password_hash(raw_password, length=12)

	@classmethod
	def get_by_auth_token(cls, user_id, token, subject='auth'):
		"""Returns a user object based on a user ID and token.

		:param user_id:
			The user_id of the requesting user.
		:param token:
			The token string to be verified.
		:returns:
			A tuple ``(User, timestamp)``, with a user object and
			the token timestamp, or ``(None, None)`` if both were not found.
		"""
		token_key = cls.token_model.get_key(user_id, subject, token)
		user_key = ndb.Key(cls, user_id)
		# Use get_multi() to save a RPC call.
		valid_token, user = ndb.get_multi([token_key, user_key])
		if valid_token and user:
			timestamp = int(time.mktime(valid_token.created.timetuple()))
			return user, timestamp
		return None, None

	#Properties
	# username = db.StringProperty(required=True)
	# passHash = db.TextProperty(required=True)
	# email = db.StringProperty(required=False)
	bio = db.TextProperty(required=False)
	# created = db.DateTimeProperty(auto_now_add=True)
#Table for requests
class Request(db.Model):
	driverId = db.IntegerProperty(required=True)
	rideId = db.IntegerProperty(required=True)
	requesterId = db.IntegerProperty(required=True)
	message = db.TextProperty(required=False)
