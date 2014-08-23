'''
Created on Aug 22, 2014

@author: svatasoiu
'''
from Handler import Handler, check_login
from database import User

class Payments(Handler):
    
    @check_login
    def get(self):
        user = User.get_by_id(self.getUser())
        payments = user.payments
        
        self.render('payments.html', payments=payments)
    
    def post(self):
        pass
        