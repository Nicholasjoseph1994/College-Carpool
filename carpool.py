import sys, os
import webapp2

sys.path.append('handlers')
sys.path.append('lib')
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
from Verify import Verify
from VenmoLogOut import VenmoLogOut
from VenmoWebhook import VenmoWebhook
from AdminPage import AdminPage
from PasswordRecovery import PasswordRecovery
from UpdateVenmo import UpdateVenmo
import constants

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': constants.APP_SECRET
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
										('/verify', Verify),
                                        ('/venmo-logout', VenmoLogOut),
                                        ('/venmo-webhook', VenmoWebhook),
                                        ('/admin', AdminPage),
                                        ('/recover', PasswordRecovery),
                                        ('/update-venmo', UpdateVenmo)
										], config=config,
										debug = True)

