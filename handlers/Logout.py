from Handler import Handler
class Logout(Handler):
    def get(self):
        self.response.delete_cookie('user')
        self.session['channel_token'] = None
        self.redirect("/venmo-logout?next=/login")
