'''
Created on Aug 19, 2014

@author: svatasoiu
'''
from Handler import Handler
from database import *

class VenmoWebhook(Handler):
    def get(self):
        self.response.write(self.request.get('venmo_challenge'))
    
    def post(self):
        date = self.response.get('date_created')
        type = self.response.get('type')
        data = self.response.get('data')
        
        if type == "payment.created":
            payment = Payment(type="Venmo", dateCreated=date, lastUpdated=date, status=data.get('status'),
                              payerID=data.get('actor').get('user').get('id'), 
                              apiID=data.get('id'),
                              receiverID=data.get('target').get('user').get('id'),
                              amount=data.get('amount'), note=data.get('note'))
            payment.put()
        elif type == "payment.updated":
            status = data.get('status')
            payment = Payment.gql("where apiID=" + data.get('id'))
            payment.status = status
            payment.lastUpdated = date # need to check that this is working properly
            
            # add in logic for payment processing
            # check the status and update user/ride info accordingly
            self.processPayment(status)
            payment.put()
    
    def processPayment(self, status):
        if status == "settled": 
            # fully accept passenger, send email out to both parties
            pass
        elif status in ["cancelled","expired","failed"]: 
            # archive payment
            # notify driver
            pass
        elif status == "pending":
            pass
        else:
            pass