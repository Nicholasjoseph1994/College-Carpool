'''
Created on Aug 19, 2014

@author: svatasoiu
'''
from Handler import Handler
from google.appengine.api import mail
from database import Ride, User, Payment
import re

class VenmoWebhook(Handler):
    def get(self):
        self.response.write(self.request.get('venmo_challenge'))
    
    def post(self):
        date = self.response.get('date_created')
        updateType = self.response.get('type')
        data = self.response.get('data')
        driverID = data.get('target').get('user').get('id')
        passengerID = data.get('actor').get('user').get('id')
        if updateType == "payment.created":
            payment = Payment(type="Venmo", dateCreated=date, lastUpdated=date, status=data.get('status'),
                              payerID=passengerID, 
                              apiID=data.get('id'),
                              receiverID=driverID,
                              amount=data.get('amount'), note=data.get('note'))
            payment.put()
        elif updateType == "payment.updated":
            status = data.get('status')
            payment = Payment.gql("WHERE apiID=" + data.get('id'))
            payment.status = status
            payment.lastUpdated = date # need to check that this is working properly
            
            # add in logic for payment processing
            # check the status and update user/ride info accordingly
            self.processPayment(data, status, driverID, passengerID)
            payment.put()
    
    def processPayment(self, data, status, driverID, passengerID):
        driver = User.gql("WHERE venmoID=" + str(driverID))
        passenger = User.gql("WHERE venmoID=" + str(passengerID))
        if status == "settled": 
            # fully accept passenger, send email out to both parties
            note = data.get('note')
            # get ride ID from note
            m = re.search("[(]Ride #(?P<rideID>\d+)[)]", note)
            if m:
                rideID = m.group("rideID")
                ride = Ride.get_by_id(rideID)
                # add passenger to passIDs
                ride.addPassenger(passenger.key().id())
                ride.put()
                
                # send emails to both parties
                sender_address = "notifications@college-carpool.appspotmail.com"
                subject = "Have a safe upcoming drive!"
                body = \
                    """Thank you for using college-carpool. You are driving with %s from %s to %s. 
                    Reach out to your driver at %s
                    """ % (driver.username, ride.start, ride.destination, driver.email)
                mail.send_mail(sender_address, passenger.email, subject, body)
                
                subject = "Passenger Added!"
                body = "%s (%s) successfully paid for your ride from %s to %s" \
                    % (passenger.username, passenger.email, ride.start, ride.destination)
                mail.send_mail(sender_address, driver.email, subject, body)
                
                # send notification through channel
        elif status in ["cancelled","expired","failed"]: 
            # archive payment because payment failed
            # notify driver
            subject = "Passenger Payment Failed!"
            body = "%s payment for your ride from %s to %s failed" % (passenger.username, ride.start, ride.destination)
            mail.send_mail(sender_address, driver.email, subject, body)
            
            # send notification through channel
        elif status == "pending":
            pass
        else:
            pass