import webapp2
import os
import jinja2
import validation
from functools import wraps
from database import *
from google.appengine.api import mail, channel, memcache
from webapp2_extras import sessions, sessions_memcache
import datetime
import urllib
import json
import constants

#Lines for using HTML templates
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    def dispatch(self):
        """Get a session store for this request."""
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key."""
        return self.session_store.get_session(name='mc_session',
            factory=sessions_memcache.MemcacheSessionFactory)

    #Writes to the page
    def write(self, *a, **kw):
        """Writes to the page."""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Returns as a string the html of the page."""
        t = JINJA_ENV.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """Renders the page."""
        try:
            user = User.get_by_id(self.getUser())
            username = user.username
            # get notification_count
            notification_count = user.passenger_requests.count() + user.driver_responses.count()

            if memcache.get('signed_into_venmo'):
                venmo_username = memcache.get('venmo_username')

                venmo_token = memcache.get('venmo_token')

                self.write(self.render_str(template, 
                                           username=username,
                                           token=self.session.get('channel_token'),
                                           notification_count=notification_count,
                                           CLIENT_ID=constants.CLIENT_ID,
                                           venmo_username=venmo_username,
                                           venmo_token=venmo_token,
                                           **kw))
            else:
                self.write(self.render_str(template,
                                           username=username,
                                           token=self.session.get('channel_token'),
                                           notification_count=notification_count,
                                           CLIENT_ID=constants.CLIENT_ID,
                                           **kw))
        except Exception as exc:
            print str(exc)
            self.write(self.render_str(template, **kw))

    def getUser(self):
        """Returns the id of the current user if logged in else None."""
        user_id = self.request.cookies.get('user')
        if user_id:
            user_id = validation.check_secure_val(user_id)
            if user_id:
                user_id = int(user_id)

        # create channel if not already created
        channel_token = self.session.get('channel_token')
        if user_id and channel_token is None:
            channel_token = channel.create_channel(str(user_id),
                                                   duration_minutes=1440)
            #self.response.set_cookie('channel_token', channel_token)
            self.session['channel_token'] = channel_token
            print str(user_id) + " created channel w/ token= " + channel_token

        return user_id

    def checkLogin(self, validate=True):
        """Checks if user is logged in and redirects to login page if not."""
        user_id = self.getUser()
        if user_id:
            user = User.get_by_id(user_id)
            if not user_id or not user:
                self.redirect('/login')
                return False
            elif validate and not user.activated:
                self.redirect('/verify')
                return False
        else:
            self.redirect('/login')
            return False
        return True

    def deleteOldRides(self):
        """Deletes past rides."""
        rides = [ride for ride in Ride.all() 
		         if ride.startTime < datetime.datetime.now()]
        for ride in rides:
            for request in Request.all():
                if request.rideId == ride.key().id():
                    request.delete()
            ride.delete()

    def sendActivationEmail(self, email, code):
        message = mail.EmailMessage()
        message.sender = "notifications@college-carpool.appspotmail.com"
        message.to = email
        message.subject = "Thank you for signing up with College Carpool!"
        message.body = "Thank you for using college-carpool. In order to activate your account, please go to this link:\n\n %s" \
            % (self.getVerifyURL(code))
        print message.body
        message.Send()

    def getVerifyURL(self, code):
        return "http://%s/%s?code=%s" % (self.request.host, 'verify', code)

    def getLocationInfo(self, start, destination):
        orig_coord = start.coordinates
        dest_coord = destination.coordinates
        url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_coord),str(dest_coord))
        rideStats= json.load(urllib.urlopen(url))
        rideDuration = rideStats['rows'][0]['elements'][0]['duration']['value']
        rideDistanceMeters = rideStats['rows'][0]['elements'][0]['distance']['value']
        rideDistance = (rideDistanceMeters * 0.000621371)
        rideDistance -= rideDistance % .1 #truncates to 1 digit
        rideStats['rows'][0]['elements'][0]['distance']['value'] = rideDistance
        return rideStats['rows'][0]['elements'][0]

def check_login(*outer_args):
    validate = True
    def decorator(view_func):
        def wrapper(self, *args, **kwargs):
            if not self.checkLogin(validate=validate):
                return
            else:
                return view_func(self, *args, **kwargs)
        return wrapper

    if len(outer_args) == 1 and callable(outer_args[0]):
        return decorator(outer_args[0])
    else:
        validate = outer_args[0]
        return decorator
