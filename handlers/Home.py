from google.appengine.ext import db
from Handler import Handler, check_login
from database import *
import time

class Home(Handler):
    @check_login
    def get(self):
        self.deleteOldRides()
        
        #Rides
        user = User.get_by_id(self.getUser())
        rides = user.rides
        
        #note: sort this later
        for ride in rides:
            driver = ride.driver
            ride.driverName = driver.username
            ride.driverEmail = driver.email
                
        #Requests
        requests = list(user.requests_passenger)
        self.render("home.html", rides=rides, requests=requests)

    def post(self):
        """This is for if they are cancelling a ride."""
        ride = Ride.get_by_id(int(self.request.get("rideId")))
        ride.archive()
        time.sleep(0.25)
        self.redirect('home')
