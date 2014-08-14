'''
Created on Aug 14, 2014

@author: svatasoiu
'''
from Handler import Handler
from google.appengine.api import memcache

class VenmoLogOut(Handler):
    def get(self):
        memcache.add('signed_into_venmo', False)
        memcache.delete('venmo_token')
        memcache.delete('venmo_username')
        memcache.delete('venmo_balance')
        memcache.delete('AUTHORIZATION_CODE')
        nextURL = self.request.get('next')
        self.redirect(nextURL if nextURL else '/home')