from google.appengine.ext import db

#from django.core.urlresolvers import reverse
from Handler import Handler
from database import *
import validation

class Signup(Handler):
	#Writes the form with the rides passed as a parameter for the map
	def write_form(self, userError="", passError="", verifyError="", emailError="", username="", email="", bio=""):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		# need to get just a few, perhaps 10-20
		self.render("signup.html", rides=rides, userError=userError, passError=passError, verifyError=verifyError, emailError=emailError, username=username, email=email, bio=bio)
	def get(self):
		self.write_form()
	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')
		bio = self.request.get('bio')

		username = validation.username(user_username)
		password = validation.password(user_password)
		verify = validation.verify(user_verify, user_password)
		email = validation.email(user_email)

		userError=""
		passError=""
		verifyError=""
		emailError=""
		if not username:
			userError = "That's not a valid username."
			user_username=""
		if not password:
			passError = "That wasn't a valid password."
		if not verify:
			verifyError = "Your passwords didn't match."
		if not email:
			emailError = "That's not a valid email."
			user_email=""

		if username and password and verify and email:
			passHash = validation.make_pw_hash(username, password)
			code = validation.make_salt()

			user= User(username = username, passHash = passHash, email = email, bio=bio, activationCode=code)
			u = User.all().filter('username =', username).get()
			if u:
				self.write_form("That username is already taken.", passError, verifyError, emailError, "", user_email, bio=bio)
				return
			user_id = user.put().id()
			self.response.headers['Content-Type'] = 'text/plain'
			cookie_val = validation.make_secure_val(str(user_id))
			self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
			self.sendActivationEmail(email, code)
			self.redirect("/home")
		else:
			self.write_form(userError, passError, verifyError, emailError, user_username, user_email, bio=bio)

