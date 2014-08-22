from google.appengine.ext import db
from Handler import Handler
import validation

class Login(Handler):
    def write_form(self, username="", error=""):
        rides = list(db.GqlQuery("SELECT * FROM Ride"))
        self.render("login.html", rides=rides, username=username, error=error)

    def get(self):
        """Renders the form with no error messages."""
        self.write_form()

    def post(self):
        """Deals with submitting the form."""
        #Get information from the post request
        username = self.request.get("username")
        password = self.request.get("password")
        user = db.GqlQuery('SELECT * FROM User WHERE username=:username',
                           username=username).get()
        if user:
            #checks if the username and password are valid
            if validation.valid_pw(user.username, password, user.passHash):
                user_id = user.key().id()
                #Makes and adds the cookie
                self.response.headers['Content-Type'] = 'text/plain'
                cookie_val = validation.make_secure_val(str(user_id))
                self.response.headers.add_header('Set-Cookie',str('user=%s; Path=/' % cookie_val))
                self.redirect("home")
            else:
                self.write_form(error="Invalid Password", username=username)
        else:
            self.write_form(error="User doesn't exist")
