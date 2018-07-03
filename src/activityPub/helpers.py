from models.base import BaseModel
from settings import (DOMAIN, SCHEME)
from urls import urls

def reverse_uri(name, *args):
    return urls[name].format(**args[0])

def uri(name, *args):
    path = reverse_uri(name, *args)
    return "{protocol}://{domain}{path}".format(protocol=SCHEME, domain=DOMAIN, path=path)

class URIs(object):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
