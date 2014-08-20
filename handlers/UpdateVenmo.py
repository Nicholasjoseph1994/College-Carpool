'''
Created on Aug 19, 2014

@author: svatasoiu
'''
import json
from Handler import Handler
from lib import requests

class UpdateVenmo(Handler):
    def get(self):
        response = requests.get("https://api.venmo.com/v1/me?access_token=" + self.request.get('access_token'))
        balance = response.json().get('data').get('balance')
        
        payload = {}
        payload['balance'] = balance
        self.response.write(json.dumps(payload))
    
    def post(self):
        pass