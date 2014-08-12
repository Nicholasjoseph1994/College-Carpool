from google.appengine.ext import db
from Handler import Handler
from database import *
import validation
import logging
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

class Login(Handler):
	def write_form(self, username="", error=""):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.render("login.html",  rides=rides, username=username, error=error)

	#Renders the form with no error messages
	def get(self):
		self.write_form()

	#Deals with submitting the form
	def post(self):
		#Get information from the post request
		username = self.request.get("username")
		password = self.request.get("password")
		try:
			u = self.auth.get_user_by_password(username, password, remember=True)
			self.redirect('/home')
		except (InvalidAuthIdError, InvalidPasswordError) as e:
			logging.info('Login failed for user %s because of %s', username, type(e))
			self.write_form(username=username,
					error ='Login failed for user %s because of %s' % (username, type(e)))
		# user = db.GqlQuery('SELECT * FROM User WHERE username=:username', username=username).get()
		# if user:
		# 	if validation.valid_pw(user.username, password, user.passHash): #checks if the username and password are valid
		# 		user_id = user.key().id()
		# 		#Makes and adds the cookie
		# 		self.response.headers['Content-Type'] = 'text/plain'
		# 		cookie_val = validation.make_secure_val(str(user_id))
		# 		self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
		# 		self.redirect("home")
		# 	else:
		# 		self.write_form(error="Invalid Password", username=username)
		# else:
		# 	self.write_form(error="User doesn't exist")
