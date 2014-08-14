from google.appengine.ext import db
from Handler import Handler
from database import *
from google.appengine.api import mail, memcache, channel
import time
import logging
from lib import requests
	
class Notification(Handler):
	#Gathers requests and then displays them
	def writePage(self, error=''):
		requests = []
		for passengerNot in list(db.GqlQuery('SELECT * FROM PassengerRequestNotification WHERE driverId=:id', id=self.getUser())):
			# request from passenger: (passenger-request)
			# has a request associated with it
			try:
				request = Request.get_by_id(passengerNot.requestId)
				request.ride = Ride.get_by_id(request.rideId)
				request.requester = User.get_by_id(request.requesterId)
				requests.append(request)
			except:
				pass
			
		responses = []
		for driverNot in list(db.GqlQuery('SELECT * FROM DriverResponseNotification WHERE requesterId=:id', id=self.getUser())):
			# driver response: (accepted-ride | rejected-ride)
			# has a ride associated with it
			try:
				response = driverNot
				ride = Ride.get_by_id(driverNot.rideId)
				response.response = driverNot.type
				response.ride = ride
				responses.append(response)
			except:
				pass
		
		#requests = list(db.GqlQuery('SELECT * FROM Request WHERE driverId=:userId', userId=self.getUser()))
		#for request in requests:
		#	request.ride = Ride.get_by_id(request.rideId)
		#	request.requester = User.get_by_id(request.requesterId)
		self.render('notification.html', requests=requests, responses=responses, error=error)

	def get(self):
		self.checkLogin()
		self.writePage()

	#If the user accepts the request, it charges the user who requested
	#If the user rejects the request, it deletes the request
	def post(self):
		accepted = self.request.get("submit")
		removeResponse = self.request.get("removeResponse")
		if accepted:
			rideId = int(self.request.get("rideId"))
			requesterId = int(self.request.get("requesterId"))
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
					response = requests.post(url, payload)
					response_dict = response.json()

					user_address = User.get_by_id(self.getUser()).email
					sender_address = "notifications@college-carpool.appspotmail.com"
					subject = "Have a safe upcoming drive!"
					body = "Thank you for using college-carpool. You are driving from %s to %s" % (ride.start, ride.destination)
					mail.send_mail(sender_address,[user_address,User.get_by_id(requesterId).email],subject,body)
					#json.loads(html)
					ride.put()
					request = Request.get_by_id(int(self.request.get("requestId")))
					request.delete()
					
					# create an accepted-ride DriverResponseNotification
					notification = DriverResponseNotification(rideId=rideId, driverId=self.getUser(), requesterId=requesterId, type="accepted-ride")
					notification.put()
					
					#print "Sending response message to " + str(requesterId)
					channel.send_message(str(requesterId), "{}");
					
					time.sleep(.5)
					self.redirect("/notification")
				else:
					self.writePage(error='Please sign in with Venmo!.')
			else:
				request = Request.get_by_id(int(self.request.get("requestId")))
				request.delete()
				
				# create a rejected-ride DriverResponseNotification
				notification = DriverResponseNotification(rideId=rideId, driverId=self.getUser(), requesterId=requesterId, type="rejected-ride")
				notification.put()
				
				#print "Sending response message to " + str(requesterId)
				channel.send_message(str(requesterId), "{}");
				
				time.sleep(.5)
				self.redirect("/notification")
		elif removeResponse:
			# remove
			responseId = int(self.request.get("responseId"))
			DriverResponseNotification.get_by_id(responseId).delete()
			time.sleep(.5)
			self.redirect("/notification")
