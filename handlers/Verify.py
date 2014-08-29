'''
Created on Aug 12, 2014

@author: svatasoiu
'''
from Handler import Handler, check_login
from database import User
from time import sleep

class Verify(Handler):
    @check_login(False)
    def get(self):
        code = self.request.get("code")
        user = User.get_by_id(self.getUser())
        if not code:
            self.render("verify.html") 
        else:
            if code == user.activationCode:
                user.activated = True
                user.put()
                #self.render("verify.html", color="green", status="Successfully Verified :)")
                #sleep(2.0)
                self.response.headers.add_header('Set-Cookie', str('is_user_activated=%s; Path=/' % "True"))
                self.redirect("/view")
            else:
                self.render("verify.html", color="red", status="Not the right activation code :(")

    def post(self):
        try:
            user = User.get_by_id(self.getUser())
            self.sendActivationEmail(user.email, user.activationCode)
            self.render("verify.html", color="green", status="Email Sent")
        except:
            self.render("verify.html", color="end", status="Email failed to send")