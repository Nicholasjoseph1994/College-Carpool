'''
Created on Aug 19, 2014

@author: svatasoiu
'''
from Handler import Handler
from database import User
import validation

class AdminPage(Handler):
    def get(self):
        self.checkLogin()
        user = User.get_by_id(self.getUser())
        self.render('admin.html', user=user)
    
    def post(self):
        user = User.get_by_id(self.getUser())
        if "updatePassword" in self.request.POST:
            passwordSuccess, passwordError = "", ""
            if validation.valid_pw(user.username, self.request.get('currentPassword'), user.passHash):
                newPass = self.request.get('newPassword')
                if newPass == self.request.get('verifyNewPassword'):
                    user.passHash = validation.make_pw_hash(user.username, newPass)
                    user.put()
                    passwordSuccess = "Password Changed Successfully!"
                else:
                    passwordError = "New passwords are not the same"
            else:
                passwordError = "That is not your current password"
            self.render('admin.html', user=user, updateError=passwordError, updateSuccess=passwordSuccess)
            
        elif "otherChanges" in self.request.POST:
            user_email = self.request.get('email')
            venmo_email = self.request.get('venmo_email')
            
            email = validation.edu_email(user_email)
            venmo_email_verify = validation.email(venmo_email)
            
            emailError, venmoEmailError, updateSuccess, updateError = "", "", "", ""
            if not email:
                emailError = "That's not a valid email."
                user_email=""
            if venmo_email != "" and venmo_email_verify is None:
                venmoEmailError = "That's not a valid email. Leave empty if you don't have one"
                venmo_email=""
            
            if email and (venmoEmailError == ""):
                try:
                    user.email= user_email
                    user.venmo_email = venmo_email
                    user.bio = self.request.get('bio')
                    user.put()
                    updateSuccess = "Succesfully Updated!"
                except:
                    updateError = "Could not save changes :("
            self.render('admin.html', user=user, updateSuccess=updateSuccess, updateError=updateError,
                         emailError=emailError, venmoEmailError=venmoEmailError)