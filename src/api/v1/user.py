import json
import os
import logging
from datetime import datetime, timedelta

import falcon
from falcon_auth import BasicAuthBackend

from models.user import User
from models.token import Token
from auth import (auth_backend,loadUserPass)

class authUser(object):

    auth = {
        'backend': BasicAuthBackend(user_loader=loadUserPass)
    }

    def on_get(self, req, resp):
        user = req.context['user']

        if user.remote:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Remote user"})

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
