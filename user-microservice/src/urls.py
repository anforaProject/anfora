from utils import load_config

config = load_config()

DOMAIN = config['domain']
SCHEMA = config['schema']

urls = {
    "activity": "/@{username}/outbox/{id}",
    "outbox": "/users/{username}/outbox",
    "inbox": "/users/{username}/inbox",
    "following": "/users/{username}/following",
    "followers": "/users/{username}/followers",
    "featured": "/users/{username}/collections/featured",
    "atom": "/users/atom/{id}/",
    "sharedInbox": "/inbox",

    "photos": "/@{username}/photos",
    "status": "/p/{username}/{id}",

    "user": "/users/{username}",
    "profile_image": "/media/files/avatars/{name}",
    "media": "/media/files/max_resolution/{id}.{extension}",
    "preview": "/media/files/small/{id}.thumbnail.{extension}",
    "logout": "/logout",

    "status_client_url": "/@{username}/{id}",
    "user_client": "/@{username}"
}


def reverse_uri(name, *args):
    if len(args):
        return urls[name].format(**args[0])
    else:
        return urls[name]

def uri(name, *args):
    path = reverse_uri(name, *args)
    return "{protocol}://{domain}{path}".format(protocol=SCHEMA, domain=DOMAIN, path=path)

class URIs(object):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
