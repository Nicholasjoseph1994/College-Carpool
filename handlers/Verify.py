'''
Created on Aug 12, 2014

@author: svatasoiu
'''
from Handler import Handler
from database import User

class Verify(Handler):
    def get(self):
        self.render("verify.html")
        
    def post(self):
        user = User.get_by_id(self.getUser())
        if user.activationCode == self.request.get("code"):
            user.activated = True
            user.put()
            self.redirect("/home")
        else:
            self.render("verify.html", error="Not the right activation code :(")