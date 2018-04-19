from models.base import BaseModel
from settings import ACTIVITYPUB_DOMAIN
from uris import reverse_uri

def uri(name, *args):
    domain = ACTIVITYPUB_DOMAIN
    path = reverse_uri(name)
    return "//{domain}{path}".format(domain, path)

class URIs(object):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
