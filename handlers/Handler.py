import webapp2
import os
import jinja2
import validation
from database import *
from google.appengine.api import mail, channel, memcache
from webapp2_extras import sessions, sessions_memcache
import datetime
from lib import requests
import urllib
import json
import constants

#Lines for using HTML templates
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
	def dispatch(self):
		# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session(name='mc_session',
			factory=sessions_memcache.MemcacheSessionFactory)

	#Writes to the page
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	#Returns as a string the html of the page
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	#Renders the page
	def render(self, template, **kw):
		try:
			username = User.get_by_id(self.getUser()).username
			# get notification_count
			notification_count = \
				db.GqlQuery('SELECT * FROM PassengerRequestNotification WHERE driverId=:id', id=self.getUser()).count() + \
				db.GqlQuery('SELECT * FROM DriverResponseNotification WHERE requesterId=:id', id=self.getUser()).count()
			if memcache.get('signed_into_venmo'):
				venmo_username = memcache.get('venmo_username')
				
				# expensive, may reconsider including this
# 				response = requests.get("https://api.venmo.com/v1/me?access_token=" + memcache.get('venmo_token'))
# 				balance = response.json().get('data').get('balance')
				venmo_token = memcache.get('venmo_token')

				self.write(self.render_str(template, username=username, token=self.session.get('channel_token'), 
									notification_count=notification_count, CLIENT_ID=constants.CLIENT_ID, 
									venmo_username=venmo_username, venmo_token = venmo_token, **kw))
			else:
				self.write(self.render_str(template, username=username, token=self.session.get('channel_token'), 
									notification_count=notification_count, CLIENT_ID=constants.CLIENT_ID, **kw))
		except Exception as e:
			print str(e)
			self.write(self.render_str(template, **kw))

	#Returns the id of the current user if logged in else None
	def getUser(self):
		userId = self.request.cookies.get('user')
		if userId:
			userId = validation.check_secure_val(userId)
			if userId:
				userId = int(userId)

		# create channel is not already created
		channel_token = self.session.get('channel_token')
		if userId and channel_token is None:
			channel_token = channel.create_channel(str(userId))
			#self.response.set_cookie('channel_token', channel_token)
			self.session['channel_token'] = channel_token
			print str(userId) + " created channel w/ token= " + channel_token

		return userId

	#Checks if user is logged in and redirects to login page if not
	def checkLogin(self, validate=True):
		userID = self.getUser()
		if not userID:
			self.redirect('login')
			return
		elif validate and not User.get_by_id(userID).activated:
			self.redirect('verify')

	#Deletes past rides
	def deleteOldRides(self):
		rides = [ride for ride in Ride.all() if ride.startTime < datetime.datetime.now()]
		for ride in rides:
			for request in Request.all():
				if request.rideId == ride.key().id():
					request.delete()
			ride.delete()

	def sendActivationEmail(self, email, code):
		message = mail.EmailMessage()
		message.sender = "notifications@college-carpool.appspotmail.com"
		message.to = email
		message.subject = "Thank you for signing up with College Carpool!"
		message.body = "Thank you for using college-carpool. In order to activate your account, please go to this link:\n\n %s" \
			% (self.getVerifyURL(code))
		print message.body
		message.Send()

	def getVerifyURL(self, code):
		return "http://%s/%s?code=%s" % (self.request.host, 'verify', code)

	def getLocationInfo(self, start, destination):
		orig_coord = start.coordinates
		dest_coord = destination.coordinates
		url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_coord),str(dest_coord))
		rideStats= json.load(urllib.urlopen(url))
		rideDuration = rideStats['rows'][0]['elements'][0]['duration']['value']
		rideDistanceMeters = rideStats['rows'][0]['elements'][0]['distance']['value']
		rideDistance = (rideDistanceMeters * 0.000621371)
		rideDistance -= rideDistance % .1 #truncates to 1 digit
		rideStats['rows'][0]['elements'][0]['distance']['value'] = rideDistance
		return rideStats['rows'][0]['elements'][0]
