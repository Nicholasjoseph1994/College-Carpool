import webapp2
import os
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
class Handler(webapp2.RequestHandler):
	#writes to the page
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	#returns as a string the html of the page
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	#renders the page
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
	#returns the id of the current user
	def getUser(self):
		userId = self.request.cookies.get('user')
		if userId:
			userId = validation.check_secure_val(userId)
			if userId:
				userId = int(userId)
		return userId
	#checks if user is logged in and redirects to login page if not
	def checkLogin(self):
		if not self.getUser():
			self.redirect('login')
	#Deletes past rides
	def deleteOldRides(self):
		rides = [ride for ride in Ride.all() if ride.startTime< datetime.datetime.now()]
		for ride in rides:
			for request in Request.all():
				if request.rideId == ride.key().id():
					request.delete()
			ride.delete()
