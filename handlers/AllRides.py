from google.appengine.ext import db
from database import *
from Handler import Handler

class AllRides(Handler):
		#Displays all of the rides currently existing on a map
    def get(self):
        rides = list(db.GqlQuery("SELECT * FROM Ride"))
        self.render("manyRides.html", rides=rides)
