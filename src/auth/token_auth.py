from models.user import User 
from models.token import Token

import peewee_async
import functools
from models.base import db

import bcrypt
import base64


def loadUserToken(token, object):
    
    try:
        candidate = Token.get(key=token)
        return candidate.user
    except Token.DoesNotExist:
        return None


def bearerAuth(method):

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        auth = self.request.headers.get('Authorization')

        if auth:
            parts = auth.split()

            if parts[0].lower() != 'bearer':
                self.set_status(401)
                self.write("invalid header authorization")
                self.finish()
                return
            elif len(parts) == 1:
                self.set_status(401)
                self.write("invalid header authorization")
                self.finish()
                return
            elif len(parts) > 2:
                self.set_status(401)
                self.write("invalid header authorization")
                self.finish()
                return 
            token = parts[1]
            t = loadUserToken(token, self.application.objects)
            if not t:
                self.write("Invalid token")
                self.finish()
                return

            kwargs['user'] = t
        return method(self,*args, **kwargs)
    return wrapper

def is_authenticated(method):

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
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
            t = loadUserToken(token, self.application.objects)
            if t == None:
                authenticated = False
            else:
                kwargs['user'] = t
        else:
            authenticated = False

        kwargs['is_authenticated'] = authenticated
        return method(self,*args, **kwargs)
    return wrapper


def userPassLogin(username, password):
    candidate = User.get_or_none(username=username)
    if candidate != None:
        pw = candidate.password
        password = password.encode()
        if bcrypt.hashpw(password,pw) == pw:
            return candidate.profile.get()
        else:
            return False 

def basicAuth(method):

    def end_request(handler):
        handler.write("Invalid token")
        handler.finish()

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')

        if auth_header is None: 
            return end_request(self)
        if not auth_header.startswith('Basic '): 
            return end_request(self)

        auth_decoded = base64.decodestring(auth_header[6:].encode()).decode('utf-8')
        username, password = auth_decoded.split(':', 2)
        user = userPassLogin(username, password)

        if user:
            kwargs['user'] = user
            return method(self,*args, **kwargs)
        else:
            end_request(self)
            return 

        
    return wrapper
