import webapp2
import os
import jinja2
import validation
from database import *
import datetime

import logging
from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

#Lines for using HTML templates
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
class Handler(webapp2.RequestHandler):
	#Writes to the page
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	#Returns as a string the html of the page
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	#Renders the page
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
	#Returns the id of the current user if logged in else None
	def getUser(self):
		userId = self.request.cookies.get('user')
		if userId:
			userId = validation.check_secure_val(userId)
			if userId:
				userId = int(userId)
		return userId
	#Checks if user is logged in and redirects to login page if not
	def checkLogin(self):
		if not self.getUser():
			self.redirect('login')
	#Deletes past rides
	def deleteOldRides(self):
		rides = [ride for ride in Ride.all() if ride.startTime < datetime.datetime.now()]
		for ride in rides:
			for request in Request.all():
				if request.rideId == ride.key().id():
					request.delete()
			ride.delete()

	#Methods from http://blog.abahgat.com/2013/01/07/user-authentication-with-webapp2-on-google-app-engine
	def display_message(self, message):
		self.write(message)

	@webapp2.cached_property
	def auth(self):
		return auth.get_auth()

	@webapp2.cached_property
	def user_info(self):
		return self.auth.get_user_by_session()

	@webapp2.cached_property
	def user(self):
		u = self.user_info
		return self.user_model.get_by_id(u['user_id']) if u else None

	@webapp2.cached_property
	def user_model(self):
		return self.auth.store.user_model

	@webapp2.cached_property
	def session(self):
		return self.session_store.get_session(backend="datastore")

	def dispatch(self):

		self.session_store = sessions.get_store(request=self.request)
		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.session_store.save_sessions(self.response)
