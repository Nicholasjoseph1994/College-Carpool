from Handler import Handler
class Logout(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', str('user=; Path=/'))
		self.redirect("login")