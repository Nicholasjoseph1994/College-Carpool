import re
import hashlib
import string
import random
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]*brown\.edu$")

def username(username):
	if USER_RE.match(username):
		return username
	else:
		return None

def password(password):
	if PASS_RE.match(password):
		return password
	else:
		return None

def verify(password, verify):
	if password == verify:
		return verify
	else:
		return None

def email(email):
	if EMAIL_RE.match(email) or email == "nicholasjoseph1994@gmail.com":
		return email
	else:
		return None 

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw):
	salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
	hashh, salt = h.split('|')
	shouldbe = hashlib.sha256(name + pw + salt).hexdigest()
	return shouldbe == hashh

def hash_str(s):
	return hashlib.sha256(s).hexdigest()

def make_secure_val(s):
	return "%s|%s" %(s, hash_str(s))

def check_secure_val(h):
	if h is None: return None
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val
