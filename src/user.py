import json
import os
import logging
from datetime import datetime, timedelta

import falcon
from falcon_auth import BasicAuthBackend

from storage import (db, User, Token)
from auth import (auth_backend,loadUserPass)

class authUser(object):
    
    auth = {
        'backend': BasicAuthBackend(user_loader=loadUserPass)
    }
    
    def on_get(self, req, resp):
        user = req.context['user']        
        now = datetime.utcnow()
            
        payload = {
            'id': user.id,
            'username': user.username,
            'admin': user.admin,
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=3600*5)
        }            

        
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"token":auth_backend.get_auth_token(payload)})
