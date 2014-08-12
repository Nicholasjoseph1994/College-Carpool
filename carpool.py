import sys
import webapp2

sys.path.append('handlers')
from MainPage import MainPage
from Home import Home
from Signup import Signup
from PostRide import PostRide
from Login import Login
from Logout import Logout
from View import View
from Notification import Notification
from RidePage import RidePage
from oauthAuthentication import oauthAuthentication
from AllRides import AllRides
from Verification import Verification

config = {
  'webapp2_extras.auth': {
    'user_model': 'database.User',
    'user_attributes': ['username', 'email', 'bio']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}
application = webapp2.WSGIApplication([ ('/', MainPage),
										('/home', Home),
										('/signup', Signup),
										('/postride', PostRide),
										('/login', Login),
										('/logout', Logout),
										('/view', View),
										('/notification', Notification),
										('/(\d+)', RidePage),
										('/oauth-authorized', oauthAuthentication),
										('/allrides', AllRides),
										webapp2.Route(
											'/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
											handler=Verification,
											name='verification'
											)
										],
										config=config,
										debug = True)

