urls = {
    "activity": "/@{username}/outbox/{id}",
    "outbox": "/users/{username}/outbox",
    "inbox": "/users/{username}/inbox",
    "following": "/users/{username}/following",
    "followers": "/users/{username}/followers",
    "featured": "/users/{username}/collections/featured",
    "atom": "/users/atom/{id}/",
    "sharedInbox": "/inbox"

    "photos": "/@{username}/photos",
    "status": "/p/{username}/{id}",

    "user": "/users/{username}",
    "profile_image": "/media/files/avatars/{name}",
    "media": "/media/files/max_resolution/{id}.{extension}",
    "preview": "/media/files/small/{id}.thumbnail.{extension}",
    "logout": "/logout",

    "status_client_url": "/@{username}/{id}",
    
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
