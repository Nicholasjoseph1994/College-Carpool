import webapp2
import os
import jinja2
import validation
from database import *
from google.appengine.api import mail, memcache, channel
from webapp2_extras import sessions, sessions_memcache
import datetime
import urllib
import json
import constants
import logging
from lib import requests

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
            notification_count = user.passenger_requests.count() + user.driver_responses.count() + len(user.payment_notifications)

            if self.session.get('signed_into_venmo'):
                venmo_username = self.session.get('venmo_username')
                
                venmo_token = self.session.get('venmo_token')

                self.write(self.render_str(template, username=username, token=self.session.get('channel_token'), 
                                    notification_count=notification_count, CLIENT_ID=constants.CLIENT_ID, 
                                    venmo_username=venmo_username, venmo_token = venmo_token, **kw))
            else:
                self.write(self.render_str(template, username=username, token=self.session.get('channel_token'), 
                                    notification_count=notification_count, CLIENT_ID=constants.CLIENT_ID, **kw))
        except Exception as e:
            print str(e)
            self.write(self.render_str(template, **kw))

    def getUser(self):
        """Returns the id of the current user if logged in else None."""
        userId = self.request.cookies.get('user')
        if userId:
            userId = validation.check_secure_val(userId)
            if userId:
                userId = int(userId)

        # create channel if not already created
        channel_token = self.session.get('channel_token')
        if userId and channel_token is None:
            cached_token = memcache.get('channel_token-' + str(userId))
            if cached_token:
                channel_token = cached_token
            else:
                channel_token = channel.create_channel(str(userId), duration_minutes=1440)
                print str(userId) + " created channel w/ token= " + channel_token
                memcache.add('channel_token-' + str(userId), channel_token)
                
            self.session['channel_token'] = channel_token

        return userId

    def checkLogin(self, validate=True):
        """Checks if user is logged in and redirects to login page if not."""
        userID = self.getUser()
        next_url = self.request.path
        if userID:
            is_user_activated = self.request.cookies.get('is_user_activated')
            
            if not userID:
                self.redirect('/login?next=' + next_url)
                return False
            elif validate and is_user_activated != "True":
                self.redirect('/verify')
                return False
        else:
            self.redirect('/login?next=' + next_url)
            return False
        return True

    def deleteOldRides(self):
        """Deletes past rides."""
        now = datetime.datetime.now()
        rides = Ride.all().filter("startTime < ", now) #[ride for ride in Ride.all() if ride.startTime < now]
        for ride in rides:
            ride.archive()

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
    
    def payForRide(self, ride, passenger):
        driver = ride.driver
        ride.addPassenger(passenger)
                    
        access_token = self.session.get('venmo_token')
        note = "Spent this money on carpooling with college-carpool.appspot.com (Ride #%s)" % (ride.key().id())
                    
        venmo_email = driver.venmo_email
        email = venmo_email if venmo_email else driver.email
        amount = ride.cost
        payload = {
            "access_token":access_token,
            "note":note,
            "amount":amount,
            "email":email
        }
        print amount, access_token, email
        logging.error(amount)
        url = "https://api.venmo.com/v1/payments"
        response = requests.post(url, payload)
        
        # check response
        response_dict = response.json()

        sender_address = "notifications@college-carpool.appspotmail.com"
        subject = "Have a safe upcoming drive!"
        body = "Thank you for using college-carpool. You are driving from %s to %s. You will receive a payment confirmation soon" \
             % (ride.start, ride.destination)
        mail.send_mail(sender_address,[driver.email, passenger.email],subject,body)
        ride.put()
                    
        request = Request.get_by_id(int(self.request.get("requestId")))
        request.archive() #.delete()
        
        return True

def check_login(*outer_args):
    validate = True
    def decorator(view_func):
        def wrapper(self, *args, **kwargs):
            # get next url parameter
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
