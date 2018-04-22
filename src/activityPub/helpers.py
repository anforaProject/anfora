from models.base import BaseModel
from settings import (ACTIVITYPUB_DOMAIN, protocol)
from urls import urls

def reverse_uri(name, *args):
    return urls[name].format(**args[0])

def uri(name, *args):
    domain = ACTIVITYPUB_DOMAIN
    path = reverse_uri(name, *args)
    return "{protocol}://{domain}{path}".format(protocol=protocol, domain=domain, path=path)

class URIs(object):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
