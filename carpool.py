import os
import webapp2
import jinja2
import validation
import json
import time
import logging
import datetime
import urllib
import urllib2
import cookielib
import socket
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from constants import CONSUMER_ID, CONSUMER_SECRET, APP_SECRET

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

###########################################################################
#######                       Database Classes:                     #######
###########################################################################

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
class User(db.Model):
	username = db.StringProperty(required=True)
	passHash = db.TextProperty(required=True)
	email = db.StringProperty(required=False)
	bio = db.TextProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
#Table for requests
class Request(db.Model):
	driverId = db.IntegerProperty(required=True)
	rideId = db.IntegerProperty(required=True)
	requesterId = db.IntegerProperty(required=True)
	message = db.TextProperty(required=False)

###########################################################################
#######                       Handler Classes:                      #######
###########################################################################

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
	def escapeJson(self, page):
		for index, i in enumerate(page):
			if i == "\"":
				page = page[:index] + "\\" + page[index:]
		return page
	def getUser(self):
		userId = self.request.cookies.get('user')
		if userId:
			userId = validation.check_secure_val(userId)
			if userId:
				userId = int(userId)
		return userId
	def userLoggedIn(self):
		return True if self.getUser() else False
class Login(Handler):
	def write_form(self, username="", error=""):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.render("login.html",  rides=rides, username=username, error=error)

	#Renders the form with no error messages
	def get(self):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.render("login.html", rides=rides)

	#Deals with submitting the form
	def post(self):
		#Get information from the post request
		username = self.request.get("username")
		password = self.request.get("password")
		userQuery = db.GqlQuery('SELECT * FROM User WHERE username=:username', username=username) #Does Query
		userQuery = list(userQuery)
		if len(userQuery)>0: #if the user exists
			user = userQuery[0]
			if validation.valid_pw(user.username, password, user.passHash): #checks if the username and password are valid
				user_id = user.key().id()
				#Makes and adds the cookie
				self.response.headers['Content-Type'] = 'text/plain'
				cookie_val = validation.make_secure_val(str(user_id))
				self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
				self.redirect("home")
			else:
				self.write_form(error="Invalid Password", username=username)
		else:
			self.write_form(error="User doesn't exist")

class Home(Handler):
	def render_front(self, rides, requests):
		self.render("home.html", rides=rides, requests=requests)
	def get(self):
		if memcache.get('venmo_token'):
			data = {'name': memcache.get('venmo_username'),
					'consumer_id': CONSUMER_ID,
					'access_token': memcache.get('venmo_token'),
					'signed_into_venmo': True}
		else:
			data = {'signed_into_venmo': False,
					'consumer_id': CONSUMER_ID}

		#Rides
		rides = list(Ride.all())
		userId = self.getUser()
		#note: sort this later
		if len(rides)>0:
			rides = filter(lambda x: x.driverId == userId or (x.passIds and str(userId) in x.passIds), rides)
		for ride in rides:
			driver = User.get_by_id(ride.driverId)
			driverName = driver.username
			driverEmail = driver.email
			ride.driverName = driverName
			ride.driverEmail = driverEmail
			if ride.passIds:
				ride.passengers = map(User.get_by_id,map(int,ride.passIds.split(",")))
		#Requests
		requests = list(db.GqlQuery('SELECT * FROM Request WHERE requesterId=:userId', userId = userId))
		for request in requests:
			ride = Ride.get_by_id(request.rideId)
			ride.driverName = User.get_by_id(ride.driverId).username
			ride.driverEmail = User.get_by_id(ride.driverId).email
			request.ride = ride
		self.render_front(rides, requests)
class Logout(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', str('user=; Path=/'))
		self.redirect("login")
class PostRide(Handler):
	def render_front(self, start="", destination="", startTime="", cost="", passengerMax="", error=""):
		self.render("postRide.html", start=start, destination=destination, startTime=startTime, cost=cost, passengerMax=passengerMax, error=error)
	def get(self):
		self.render_front()
	def post(self):
		start = self.request.get("start")
		destination = self.request.get("destination")
		cost = float(self.request.get("cost"))
		passengerMax = int(self.request.get("passengerMax"))
		driverId = self.request.cookies.get('user')
		if driverId:
			driverId = validation.check_secure_val(driverId)
			if driverId:
				driverId = int(driverId)
		#date time stuff
		date = map(int, self.request.get("date").split("/",2))
		timeFull = self.request.get("time").split(" ")
		time = map(int, timeFull[0].split(":"))

		if "PM" in time:
			time[0] += 12

		startTime = datetime.datetime(date[2],date[0],date[1],time[0],time[1],0)

		if start and destination and startTime and cost and passengerMax:
			ride = Ride(start=start, destination=destination, startTime=startTime, cost=cost, passengerMax=passengerMax, driverId = driverId, passIds="")
			ride.put()

			self.redirect("home")
		else:
			error = "Please fill out all the fields!"
			self.render_front(start, destination, startTime, cost, passengerMax, error)
class Notification(Handler):
	def writePage(self, error=''):
		requests = list(db.GqlQuery('SELECT * FROM Request WHERE driverId=:userId', userId=self.getUser()))
		for request in requests:
			request.ride = Ride.get_by_id(request.rideId)
			request.requester = User.get_by_id(request.requesterId)
		self.render('notification.html', requests=requests, error=error)
	def get(self):
		self.writePage()
	def post(self):
		rideId = int(self.request.get("rideId"))
		requesterId = int(self.request.get("requesterId"))
		accepted = self.request.get("submit")
		if accepted == 'true':
			if memcache.get('venmo_token'):
				ride = Ride.get_by_id(rideId)
				if ride.passIds:
					passIds = ride.passIds.split(',')
				else:
					passIds = []
				passIds.append(str(requesterId))
				ride.passIds = ','.join(passIds)
				access_token = memcache.get('venmo_token')
				note = "Spent this money on carpooling with college-carpool.appspot.com"
				email = User.get_by_id(ride.driverId).email
				amount = ride.cost
				payload = {
						"access_token":access_token,
						"note":note,
						"amount":amount,
						"email":email
				}
				print amount, access_token, email
				logging.error(amount)
				url = "https://api.venmo.com/v1/payments"
				# setup socket connection timeout
				timeout = 15
				socket.setdefaulttimeout(timeout)
				# setup cookie handler
				cookie_jar = cookielib.LWPCookieJar()
				cookie = urllib2.HTTPCookieProcessor(cookie_jar)
				# create an urllib2 opener()
				opener = urllib2.build_opener(cookie) # we are not going to use proxy now
				# send payload
				req = urllib2.Request(url, urllib.urlencode(payload))
				# receive confirmation
				res = opener.open(req)
				#html = res.read()
				user_address = User.get_by_id(self.getUser()).email
				sender_address = "notifications@college-carpool.appspotmail.com"
				subject = "Have a safe upcoming drive!"
				body = "Thank you for using college-carpool. You are driving from %s to %s" % (ride.    start, ride.destination)
				mail.send_mail(sender_address,[user_address,User.get_by_id(requesterId).email],subject,body)
				#json.loads(html)
				ride.put()
				request = Request.get_by_id(int(self.request.get("requestId")))
				request.delete()
				time.sleep(.25)
				self.redirect("/notification")
			else:
				self.writePage(error='Please sign in with Venmo!.')
		else:
			request = Request.get_by_id(int(self.request.get("requestId")))
			request.delete()
			time.sleep(.25)
			self.redirect("/notification")
class oauthAuthentication(Handler):
	def get(self):
		AUTHORIZATION_CODE = self.request.get('code')
		data = {
				"client_id":CONSUMER_ID,
				"client_secret":CONSUMER_SECRET,
				"code":AUTHORIZATION_CODE
		}
		url = "https://api.venmo.com/v1/oauth/access_token"

		# setup socket connection timeout
		timeout = 15
		socket.setdefaulttimeout(timeout)
		# setup cookie handler
		cookie_jar = cookielib.LWPCookieJar()
		cookie = urllib2.HTTPCookieProcessor(cookie_jar)

		# create an urllib2 opener()
		opener = urllib2.build_opener(cookie) # we are not going to use proxy now

		# create your HTTP request
		req = urllib2.Request(url, urllib.urlencode(data))

		# submit your request
		res = opener.open(req)
		html = res.read()
		js = json.loads(html)
		access_token = js.get('access_token')
		user = js.get('user').get('username')
		memcache.add('venmo_token', access_token)
		memcache.add('venmo_username', user)
		return self.redirect("home")
	def post(self):
		pass
class Signup(Handler):
	def write_form(self, rides, userError = "", passError = "", verifyError = "", emailError = "", username = "", email=""):
		self.render("signup.html", rides=rides, userError=userError, passError=passError, verifyError=verifyError, emailError=emailError, username=username, email=email)
	def get(self):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.write_form(rides)
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
		if not password:
			passError = "That wasn't a valid password."
		if not verify:
			verifyError = "Your passwords didn't match."
		if not email:
			emailError = "That's not a valid email."

		if username and password and verify and email and bio:
			passHash = validation.make_pw_hash(username, password)
			user= User(username = username, passHash = passHash, email = email, bio=bio)
			u = User.all().filter('username =', username).get()
			if u:
				rides = list(db.GqlQuery("SELECT * FROM Ride"))
				self.write_form(rides, "That username is already taken.", passError, verifyError, emailError, username, email)
				return
			user_id = user.put().id()
			self.response.headers['Content-Type'] = 'text/plain'
			cookie_val = validation.make_secure_val(str(user_id))
			self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
			self.redirect("/home")
		else:
			rides = list(db.GqlQuery("SELECT * FROM Ride"))
			self.write_form(rides, userError, passError, verifyError, emailError, username, email)
class View(Handler):
	def get(self):
		rides = list(db.GqlQuery("SELECT * FROM Ride ORDER BY startTime DESC", userId=self.getUser()))
		rides = filter(lambda x: x.driverId!=self.getUser() and str(self.getUser()) not in x.passIds, rides)
		requests = list(db.GqlQuery("SELECT * FROM Request WHERE requesterId = :userId", userId=self.getUser()))
		requests = [x.rideId for x in requests]
		rides = [x for x in rides if x.key().id() not in requests]
		for ride in rides:
			ride.driverName = User.get_by_id(ride.driverId).username
		rides = sorted(rides, key=lambda x:x.startTime)
		self.render("rideSearch.html", rides=rides)
	def post(self):
		self.redirect('/'+self.request.get('rideId'))
#		request = Request(driverId=int(self.request.get("driverId")), rideId=int(self.request.get("rideId")), requesterId=self.getUser(), message=self.request.get("message"))
#		request.put()
#		time.sleep(.25)
#		self.redirect("/view")
class RidePage(Handler):
	def get(self, rideId):
		ride = Ride.get_by_id(int(rideId))
		ride.driverName = User.get_by_id(ride.driverId).username
		self.render("ride.html", ride=ride)
	def post(self, rideId):
		request = Request(driverId=int(self.request.get('driverId')), rideId=int(self.request.get('rideId')), requesterId=self.getUser(), message=self.request.get('message'))
		request.put()
		time.sleep(.5)
		self.redirect("/home")
class AllRides(Handler):
	def get(self):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.render("manyRides.html", rides=rides)
class MainPage(Handler):
	def get(self):
		self.redirect("/login")
application = webapp2.WSGIApplication([ ('/', MainPage),
										('/home', Home),
										('/signup', Signup),
										('/postride', PostRide),
										('/login', Login),
										('/logout', Logout),
										('/view', View),
										('/notification', Notification),
										('/(\d+)', RidePage),
										('/oauth-authorized', oauthAuthentication),
										('/allrides', AllRides)
										], debug = True)

