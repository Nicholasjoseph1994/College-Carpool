from Handler import Handler, check_login
from database import *
from google.appengine.api import mail, channel
import time
import logging
from lib import requests

class Notification(Handler):
	#Gathers requests and then displays them
	def writePage(self, error=''):
		# retrieve any requests from other users
		user = User.get_by_id(self.getUser())
		requests = list(user.passenger_requests)

		# retrieve any response notifications from other users
		responses = list(user.driver_responses)
		
		# retrieve pending payments
		payments = user.getAllPaymentNotifications()
		
		self.render('notification.html', 
				requests=requests, responses=responses, 
				payments=payments, error=error)

	@check_login
	def get(self):
		self.writePage()

	#If the user accepts the request, it charges the user who requested
	#If the user rejects the request, it deletes the request
	def post(self):
		accepted = self.request.get("submit")
		removeResponse = self.request.get("removeResponse")
		removePayment = self.request.get("removePayment")
		if accepted:
			rideId = int(self.request.get("rideId"))
			requesterId = int(self.request.get("requesterId"))
			
			ride = Ride.get_by_id(rideId)
			driver = ride.driver
			passenger = User.get_by_id(requesterId)
			
			if accepted == 'true':
				if self.session.get('venmo_token'):
					ride.addPassenger(passenger)
					
					access_token = self.session.get('venmo_token')
					note = "Spent this money on carpooling with college-carpool.appspot.com (Ride #%s)" % (ride.key().id())
					
					venmo_email = driver.venmo_email
					email = venmo_email if venmo_email else driver.email
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

					sender_address = "notifications@college-carpool.appspotmail.com"
					subject = "Have a safe upcoming drive!"
					body = "Thank you for using college-carpool. You are driving from %s to %s" % (ride.start, ride.destination)
					mail.send_mail(sender_address,[driver.email, passenger.email],subject,body)
					ride.put()
					
					request = Request.get_by_id(int(self.request.get("requestId")))
					request.archive() #.delete()
					
					# create an accepted-ride DriverResponseNotification
					notification = DriverResponseNotification(ride=ride, driver=driver, passenger=passenger, type="accepted-ride")
					notification.put()
					
					#print "Sending response message to " + str(requesterId)
					channel.send_message(str(requesterId), "{}");
					
					time.sleep(.5)
					self.redirect("/notification")
				else:
					self.writePage(error='Please sign in with Venmo!.')
			else:
				request = Request.get_by_id(int(self.request.get("requestId")))
				request.archive() #.delete()
				
				# create a rejected-ride DriverResponseNotification
				notification = DriverResponseNotification(ride=ride, driver=driver, passenger=passenger, type="rejected-ride")
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
		elif removePayment:
			# remove
			paymentId = int(self.request.get("paymentId"))
			PaymentNotification.get_by_id(paymentId).delete()
			time.sleep(.5)
			self.redirect("/notification")
