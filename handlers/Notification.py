from Handler import Handler, check_login
from database import *
from google.appengine.api import channel
import time

class Notification(Handler):
	#Gathers requests and then displays them
	def writePage(self, error=''):
		# retrieve any requests from other users
		user = User.get_by_id(self.getUser())
		requests = list(user.passenger_requests)

		# retrieve any response notifications from other users
		responses = list(user.driver_responses)
		
		# retrieve pending payments
		payments = user.payment_notifications
		
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
		pay = self.request.get("pay")
		
		if accepted:
			# done by driver
			pRequestNot = PassengerRequestNotification.get_by_id(int(self.request.get("pRequestId")))
			request = pRequestNot.request
			
			ride = request.ride
			passenger = request.passenger
			
			if accepted == 'true':
				pRequestNot.delete()
				
				# create an accepted-ride DriverResponseNotification
				notification = DriverResponseNotification(ride=ride, passenger=passenger, type="accepted-ride")
				notification.put()

				channel.send_message(str(passenger.key().id()), "{}");
			else:
				request.archive()
				
				# create a rejected-ride DriverResponseNotification
				notification = DriverResponseNotification(ride=ride, passenger=passenger, type="rejected-ride")
				notification.put()
				
				#print "Sending response message to " + str(requesterId)
				channel.send_message(str(passenger.key().id()), "{}");
		elif pay:
			# done by passenger
			responseId = int(self.request.get("responseId"))
			response = DriverResponseNotification.get_by_id(responseId)
			
			if self.session.get('venmo_token'):
				payment_response = self.payForRide(response.ride, response.passenger)
				if payment_response:
					response.delete()
				else:
					self.writePage(error='Something went wrong.')
					return
			else:
				self.writePage(error='Please sign in with Venmo!')
				return
		elif removeResponse:
			# remove
			responseId = int(self.request.get("responseId"))
			DriverResponseNotification.get_by_id(responseId).delete()
		elif removePayment:
			# remove
			paymentId = int(self.request.get("paymentId"))
			PaymentNotification.get_by_id(paymentId).delete()
			
		time.sleep(.25)
		self.redirect("/notification")
