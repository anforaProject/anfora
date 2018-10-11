from models.user import User 
from models.token import Token

import peewee_async
import functools
from models.base import db

async def loadUserToken(token, object):
    
    try:
        candidate = await object.get(Token, key=token)
        return candidate.user
    except Token.DoesNotExist:
        return None


def bearerAuth(method):

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        auth = self.request.headers.get('Authorization')

        if auth:
            parts = auth.split()

            if parts[0].lower() != 'bearer':
                handler._transforms = []
                handler.set_status(401)
                handler.write("invalid header authorization")
                handler.finish()
            elif len(parts) == 1:
                handler._transforms = []
                handler.set_status(401)
                handler.write("invalid header authorization")
                handler.finish()
            elif len(parts) > 2:
                handler._transforms = []
                handler.set_status(401)
                handler.write("invalid header authorization")
                handler.finish()

            token = parts[1]
            t = await loadUserToken(token, self.application.objects)
            if not t:
                handler.write("Invalid token")
                handler.finish()
            kwargs['user'] = t
        return method(self,*args, **kwargs)
    return wrapper

def is_authenticated(method):

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        auth = self.request.headers.get('Authorization')
        authenticated = True
        kwargs['user'] = None
        if auth:
            parts = auth.split()
            if parts[0].lower() != 'bearer':
                authenticated = False
            elif len(parts) == 1:
                authenticated = False
            elif len(parts) > 2:
                authenticated = False

            token = parts[1]
            t = await loadUserToken(token, self.application.objects)
            if t == None:
                authenticated = False
            else:
                kwargs['user'] = t
        else:
            authenticated = False

        kwargs['is_authenticated'] = authenticated
        return method(self,*args, **kwargs)
    return wrapper
