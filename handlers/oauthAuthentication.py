from google.appengine.api import memcache
from Handler import Handler
from lib import requests
from database import User
import os, constants

class oauthAuthentication(Handler):
	def get(self):
		AUTHORIZATION_CODE = self.request.get('code')
		data = {
				"client_id": constants.CLIENT_ID,
				"client_secret": constants.CLIENT_SECRET,
				"code":AUTHORIZATION_CODE
		}
		response = requests.post("https://api.venmo.com/v1/oauth/access_token", data)
		response_dict = response.json()
		
		db_user = User.get_by_id(self.getUser())
		db_user.venmo_email = response_dict.get('user').get('email')
		db_user.put()
		
		access_token = response_dict.get('access_token')
		user = response_dict.get('user').get('username')
		balance = response_dict.get('balance')
		
		memcache.add('venmo_token', access_token)
		memcache.add('venmo_username', user)
		memcache.add('venmo_balance', balance)
		memcache.add('signed_into_venmo', True)
		memcache.add('AUTHORIZATION_CODE', AUTHORIZATION_CODE)
		
		nextURL = self.request.get('next')
		return self.redirect(nextURL if nextURL else '/home')
	def post(self):
		pass
