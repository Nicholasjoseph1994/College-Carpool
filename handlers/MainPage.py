from Handler import Handler
class MainPage(Handler):
	def get(self):
		self.redirect("/login")
