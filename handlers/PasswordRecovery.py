'''
Created on Aug 19, 2014

@author: svatasoiu
'''
from Handler import Handler
from google.appengine.api import mail
from database import User
import validation

class PasswordRecovery(Handler):    
    def get(self):
        recover, userID = False, ""
        uid = self.request.get('userID')
        code = self.request.get('code')
        
        if uid and code:
            user = User.get_by_id(int(uid))
            if user and user.recoveryCode and user.recoveryCode == code:
                # display password recovery
                recover = True
                userID = uid
                
        self.render('recover.html', recover=recover, userID=userID)
    
    def post(self):
        if "recoverUsername" in self.request.POST:
            try:
                email = self.request.get('email')
                self.recoverUsernameUsingEmail(email)
                self.render('recover.html', color="green", status="Sent recovery email to %s :)" % (email))
            except:
                self.render('recover.html', color="red", status="Could not send email to %s :("  % (email))
        elif "recoverPassword" in self.request.POST:
            try:
                username = self.request.get('username')
                email = ""
                user = None
                if username:
                    print username
                    user = User.gql("WHERE username=:username", username=username).get()
                    email = user.email
                else:
                    email = self.request.get('email')
                    user = User.gql("WHERE email=:email", email=email).get()
                
                salt = validation.make_salt(25)
                link = "http://%s/recover?userID=%s&code=%s" % (self.request.host, user.key().id(), salt)

                user.recoveryCode = salt
                user.put()
                
                self.sendPasswordRecoveryEmail(email, user, link)    
                self.render('recover.html', color="green", 
                            status="Sent recovery email to a %s account :)" % (email.split("@")[1]))
            except:
                self.render('recover.html', color="red", status="Could not send email :(")
        elif "resetPassword" in self.request.POST:
            userID = self.request.get('userID')
            user = User.get_by_id(int(userID))
            
            newPass = self.request.get('newPassword')
            passwordSuccess, passwordError = "", ""
            if newPass == self.request.get('verifyNewPassword'):
                user.passHash = validation.make_pw_hash(user.username, newPass)
                user.recoveryCode = None
                user.put()
                passwordSuccess = "Password Changed Successfully!"
                self.render('recover.html', color="green", status=passwordSuccess)
            else:
                passwordError = "New passwords are not the same"
                self.render('recover.html', color="red", status=passwordError, recover=True, userID=userID)
        
    def recoverUsernameUsingEmail(self, email):
        sender_address = "notifications@college-carpool.appspotmail.com"
        user = User.gql("WHERE email=:email", email=email).get()
        subject = "College Carpool Username Recovery"
        body = "Your College Carpool Username is: %s" % (user.username)
        print body
        mail.send_mail(sender_address, email, subject, body)
        
    def sendPasswordRecoveryEmail(self, addr, user, link):
        sender_address = "notifications@college-carpool.appspotmail.com"
        subject = "College Carpool Password Recovery"
        body = "Hi, %s. Please visit %s to reset your password." % (user.username, link)
        print body
        mail.send_mail(sender_address, addr, subject, body)
