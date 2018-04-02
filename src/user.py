import json
import os
import logging
from datetime import datetime, timedelta

import falcon
from falcon_auth import BasicAuthBackend

from storage import db, User
from auth import (auth_backend,loadUser)

class authUser(object):
    
    auth = {
        'backend': BasicAuthBackend(user_loader=loadUser)
    }
    
    def on_get(self, req, resp):
        user = req.context['user']
        print(user)
        
        now = datetime.utcnow()
        payload = {
            'user': {
                'id': user.id,
                'username': user.username,
                'admin': user.admin
            },
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=8000)
        }

        
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"token":auth_backend.get_auth_token(payload)})
