import os
import sys
import webapp2
import jinja2
import validation
import json
import time
import logging
import datetime
import urllib
import urllib2
import cookielib
import socket
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from constants import CONSUMER_ID, CONSUMER_SECRET, APP_SECRET

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

