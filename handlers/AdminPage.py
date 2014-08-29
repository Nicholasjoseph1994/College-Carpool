'''
Created on Aug 19, 2014

@author: svatasoiu
'''

import validation

from database import User
from Handler import Handler, check_login

class AdminPage(Handler):
    @check_login
    def get(self):
        user = User.get_by_id(self.getUser())
        self.render('admin.html', user=user)

    def post(self):
        user = User.get_by_id(self.getUser())
        if "updatePassword" in self.request.POST:
            password_success, password_error = "", ""
            if validation.valid_pw(user.username,
                                   self.request.get('currentPassword'),
                                   user.passHash):
                new_pass = self.request.get('new_password')
                if new_pass == self.request.get('verifyNewPassword'):
                    user.passHash = validation.make_pw_hash(
                                      user.username, new_pass)
                    user.put()
                    password_success = "Password Changed Successfully!"
                else:
                    password_error = "New passwords are not the same"
            else:
                password_error = "That is not your current password"
            self.render('admin.html',
                        user=user,
                        update_error=password_error,
                        update_success=password_success)

        elif "otherChanges" in self.request.POST:
            user_email = self.request.get('email')
            venmo_email = self.request.get('venmo_email')

            email = validation.edu_email(user_email)
            venmo_email_verify = validation.email(venmo_email)

            email_error, venmo_email_error, update_success, update_error = "", "", "", ""

            if not email:
                email_error = "That's not a valid email."
                user_email = ""
            if venmo_email != "" and venmo_email_verify is None:
                venmo_email_error = "Invalid email. This is an optional field."
                venmo_email = ""

            if email and (venmo_email_error == ""):
                try:
                    user.email = user_email
                    user.venmo_email = venmo_email
                    user.bio = self.request.get('bio')
                    user.put()
                    update_success = "Succesfully Updated!"
                except:
                    update_error = "Could not save changes :("
            self.render('admin.html', 
                        user=user,
                        update_success=update_success,
                        update_error=update_error,
                        email_error=email_error,
                        venmo_email_error=venmo_email_error)
