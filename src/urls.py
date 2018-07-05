urls = {
    "activity": "/@{username}/outbox/{id}",
    "outbox": "/users/{username}/outbox",
    "inbox": "/users/{username}/inbox",
    "photos": "/@{username}/photos",
    "photo": "/p/{username}/{id}",
    "following": "/users/{username}/following",
    "followers": "/users/{username}/followers",
    "atom": "/users/{username}.atom",
    "user": "/users/{username}",
    "profile_image": "/avatars/{name}",
    "media": "/media/files/max_resolution/{id}.jpeg",
    "preview": "/media/files/small/{id}.thumbnail",
    "logout": "/logout",
    "featured": "/users/{username}/collections/featured",
}

from models.base import BaseModel
from settings import (DOMAIN, SCHEME)

def reverse_uri(name, *args):
    return urls[name].format(**args[0])

def uri(name, *args):
    path = reverse_uri(name, *args)
    return "{protocol}://{domain}{path}".format(protocol=SCHEME, domain=DOMAIN, path=path)

class URIs(object):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
