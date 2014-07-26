
from google.appengine.ext import db
from Handler import Handler
from database import *
class oauthAuthentication(Handler):
	def get(self):
		AUTHORIZATION_CODE = self.request.get('code')
		data = {
				"client_id":CONSUMER_ID,
				"client_secret":CONSUMER_SECRET,
				"code":AUTHORIZATION_CODE
		}
		url = "https://api.venmo.com/v1/oauth/access_token"

		# setup socket connection timeout
		timeout = 15
		socket.setdefaulttimeout(timeout)
		# setup cookie handler
		cookie_jar = cookielib.LWPCookieJar()
		cookie = urllib2.HTTPCookieProcessor(cookie_jar)

		# create an urllib2 opener()
		opener = urllib2.build_opener(cookie) # we are not going to use proxy now

		# create your HTTP request
		req = urllib2.Request(url, urllib.urlencode(data))

		# submit your request
		res = opener.open(req)
		html = res.read()
		js = json.loads(html)
		access_token = js.get('access_token')
		user = js.get('user').get('username')
		memcache.add('venmo_token', access_token)
		memcache.add('venmo_username', user)
		return self.redirect("home")
	def post(self):
		pass
