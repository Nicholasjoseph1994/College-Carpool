'''
Created on Aug 19, 2014

@author: svatasoiu
'''
from Handler import Handler
from google.appengine.api import mail
from database import User, Payment
import json

class VenmoWebhook(Handler):
    def get(self):
        self.response.write(self.request.get('venmo_challenge'))
    
    def post(self):
        print "Got Venmo payment update"
        print self.request.body
        js = json.loads(self.request.body)
        
        date = js['date_created']
        updateType = js['type']
        data = js['data']
        
        if updateType == "payment.created":
            driverID = data['target']['user']['id']
            passengerID = data['actor']['id']
            driver = User.gql('WHERE venmoID=' + driverID).get()
            passenger = User.gql('WHERE venmoID=' + passengerID).get()
            
            payment = Payment(type="Venmo", dateCreated=date, lastUpdate=date, status=data['status'],
                              driver=driver, passenger=passenger, apiID=data['id'], 
                              amount=data['amount'], note=data['note'])
            payment.put()
        elif updateType == "payment.updated":
            status = data['status']
            payment = Payment.gql("WHERE apiID=" + data['id'])
            payment.status = status
            payment.lastUpdated = date # need to check that this is working properly
            
            # add in logic for payment processing
            # check the status and update user/ride info accordingly
            self.processPayment(data, status, payment)
            payment.put()
    
    def processPayment(self, data, status, payment):
        if status == "settled": 
            # fully accept passenger, send email out to both parties
            
            # get ride ID from note
            ride = payment.ride
            driver = ride.driver
            passenger = payment.passenger
            
            # add passenger to ride
            ride.addPassenger(passenger)
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
            ride = payment.ride
            driver = ride.driver
            passenger = payment.passenger 
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