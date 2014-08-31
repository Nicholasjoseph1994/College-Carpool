from Handler import Handler
from lib import requests
from database import User
import constants

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
		
		# update user venmo info like email and venmoID
		db_user = User.get_by_id(self.getUser())
		if db_user.permission == "guest":
			pass
		else:
			db_user.venmoID = int(response_dict.get('user').get('id'))
			db_user.venmo_email = response_dict.get('user').get('email')
			db_user.put()
		
		access_token = response_dict.get('access_token')
		user = response_dict.get('user').get('username')
		
		self.session['venmo_token'] = access_token
		self.session['venmo_username'] = user
		self.session['signed_into_venmo'] = True
		
		nextURL = self.request.get('next')
		return self.redirect(nextURL if nextURL else '/home')
	def post(self):
		pass
