from google.appengine.ext import db
from Handler import Handler
from database import *
import validation

class Signup(Handler):
	#Writes the form with the rides passed as a parameter for the map
	def write_form(self, userError="", passError="", verifyError="", emailError="", venmoEmailError="", 
				username="", email="", venmo_email="", bio=""):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		# need to get just a few, perhaps 10-20
		self.render("signup.html", rides=rides, userError=userError, passError=passError, verifyError=verifyError, emailError=emailError,
				venmoEmailError=venmoEmailError, username=username, email=email, venmo_email=venmo_email, bio=bio)
	
	def get(self):
		self.write_form()
	
	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')
		venmo_email = self.request.get('venmo_email')
		bio = self.request.get('bio')

		username = validation.username(user_username)
		password = validation.password(user_password)
		verify = validation.verify(user_verify, user_password)
		email = validation.edu_email(user_email)
		venmo_email_verify = validation.email(venmo_email)

		userError=""
		passError=""
		verifyError=""
		emailError=""
		venmoEmailError = ""
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
		if venmo_email != "" and venmo_email_verify is None:
			venmoEmailError = "That's not a valid email. Leave empty if you don't have one"
			venmo_email=""
		
		if username and password and verify and email and (venmoEmailError == ""):
			passHash = validation.make_pw_hash(username, password)
			code = validation.make_salt()

			user = User(username = username, passHash=passHash, email=email, bio=bio, venmo_email=venmo_email, activationCode=code)
				
			u = User.all().filter('username =', username).get()
			if u:
				self.write_form("That username is already taken.", passError, verifyError, emailError, venmoEmailError, 
							"", user_email, venmo_email, bio=bio)
				return
			user_id = user.put().id()
			self.response.headers['Content-Type'] = 'text/plain'
			cookie_val = validation.make_secure_val(str(user_id))
			self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
			self.sendActivationEmail(email, code)
			self.redirect("/home")
		else:
			self.write_form(userError, passError, verifyError, emailError, venmoEmailError,
						user_username, user_email, bio=bio)

