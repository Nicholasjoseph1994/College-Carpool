from google.appengine.ext import db
from Handler import Handler
from database import *
import validation
from google.appengine.api import mail

class Signup(Handler):
	#Writes the form with the rides passed as a parameter for the map
	def write_form(self, userError="", passError="", verifyError="", emailError="", username="", email="", bio=""):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.render("signup.html", rides=rides, userError=userError, passError=passError, verifyError=verifyError, emailError=emailError, username=username, email=email, bio=bio)

	def get(self):
		self.write_form()

	def post(self):
		#Get information from form
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')
		bio = self.request.get('bio')

		#Check that the information is valid
		username = validation.username(user_username)
		password = validation.password(user_password)
		verify = validation.verify(user_verify, user_password)
		email = validation.email(user_email)

		#If something is invalid, create the proper error
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
			# u = User.all().filter('username =', username).get()
			# #Checks if the username is taken
			# if u:
			# 	self.write_form("That username is already taken.", passError, verifyError,
			# 			emailError, "", user_email, bio=bio)
			# 	return
			# u =  User.all().filter('email =', email).get()
			# #Checks if the email is taken
			# if u:
			# 	self.write_form("That email is already taken", passError, verifyError,
			# 			emailError, username, "", bio=bio)
			# 	return

			#Adds the user
			unique_properties = ['email_address']
			user_data = self.user_model.create_user(username, unique_properties,
					email_address=email, password_raw=password, bio=bio, verified=False)
			if not user_data[0]:
				self.write_form('This username or email is taken', '', verifyError, emailError,
					user_username, user_email, bio=bio)
				return
			user = user_data[1]
			user_id = user.get_id()
			token = self.user_model.create_signup_token(user_id)
			verification_url = self.uri_for('verification', type='v', user_id=user_id,
					signup_token=token, _full=True)
			user_address = user.email_address
			sender_address = 'collegecarpooltest@gmail.com'
			subject = 'Verify your college-carpool account'
			body = 'Please verify by clicking the following link: \n %s' % verification_url
			mail.send_mail(sender = sender_address,
					to = user_address,
					subject=subject,
					body=body)
			msg = 'send an email to user in order to verify their address. \
				They will be able to do so by visiting <a href = "{url}">{url}</a>'
			self.render("emailVerification.html", msg=msg.format(url=verification_url))
			return
			# passHash = validation.make_pw_hash(username, password)
			# user= User(username = username, passHash = passHash, email = email, bio=bio)
			# user_id = user.put().id()
			# self.response.headers['Content-Type'] = 'text/plain'
			# cookie_val = validation.make_secure_val(str(user_id))
			# self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
			# self.redirect("/home")
		else:
			#Refresh page with errors
			self.write_form(userError, passError, verifyError, emailError,
					user_username, user_email, bio=bio)
