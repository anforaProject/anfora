urls = {
    "activity": "/@{username}/outbox/{id}",
    "outbox": "/users/{username}/outbox",
    "inbox": "/users/{username}/inbox",
    "photos": "/@{username}/photos",
    "status": "/p/{username}/{id}",
    "following": "/users/{username}/following",
    "followers": "/users/{username}/followers",
    "user": "/users/{username}",
    "atom": "/users/atom/{id}/",
    "profile_image": "/media/files/avatars/{name}",
    "media": "/media/files/max_resolution/{id}.{extension}",
    "preview": "/media/files/small/{id}.thumbnail.jpg",
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
