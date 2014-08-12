import webapp2
import os
import jinja2
import validation
from database import *
import datetime

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
		userID = self.getUser()
		if not userID:
			self.redirect('login')
		elif not User.get_by_id(userID).activated:
			self.redirect('verify')
	#Deletes past rides
	def deleteOldRides(self):
		rides = [ride for ride in Ride.all() if ride.startTime < datetime.datetime.now()]
		for ride in rides:
			for request in Request.all():
				if request.rideId == ride.key().id():
					request.delete()
			ride.delete()
