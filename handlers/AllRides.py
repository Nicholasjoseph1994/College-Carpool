from google.appengine.ext import db
from Handler import Handler
from database import *
class AllRides(Handler):
	def get(self):
		rides = list(db.GqlQuery("SELECT * FROM Ride"))
		self.render("manyRides.html", rides=rides)
