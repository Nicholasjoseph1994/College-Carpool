'''
Created on Aug 14, 2014

@author: svatasoiu
'''
from Handler import Handler
from google.appengine.api import memcache

class VenmoLogOut(Handler):
    def get(self):
        memcache.delete('signed_into_venmo')
        memcache.delete('venmo_token')
        memcache.delete('venmo_username')
        memcache.delete('venmo_balance')
        nextURL = self.request.get('next')
        self.redirect(nextURL if nextURL else '/home')