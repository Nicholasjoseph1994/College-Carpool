'''
Created on Aug 14, 2014

@author: svatasoiu
'''
from Handler import Handler

class VenmoLogOut(Handler):
    def get(self):
        if self.session.get('signed_into_venmo'): 
            del self.session['signed_into_venmo']
        if self.session.get('venmo_token'): 
            del self.session['venmo_token']
        if self.session.get('venmo_username'): 
            del self.session['venmo_username']
        nextURL = self.request.get('next')
        self.redirect(nextURL if nextURL else '/home')