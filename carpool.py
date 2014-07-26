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
										('/allrides', AllRides)
										], debug = True)

