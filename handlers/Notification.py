from google.appengine.ext import db
from Handler import Handler
from database import *
from google.appengine.api import mail
from google.appengine.api import memcache
import time
import socket
import logging
import urllib
import urllib2
import cookielib

class Notification(Handler):
	def writePage(self, error=''):
		requests = list(db.GqlQuery('SELECT * FROM Request WHERE driverId=:userId', userId=self.getUser()))
		for request in requests:
			request.ride = Ride.get_by_id(request.rideId)
			request.requester = User.get_by_id(request.requesterId)
		self.render('notification.html', requests=requests, error=error)
	def get(self):
		self.checkLogin()
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
