import re

from models.user import UserProfile

def extract_user(uri):

    if uri.startswith("@"):
        uri = uri[1:]
    elif uri.startswith('acct:'):
        uri = uri[5:]

    result = uri.split("@")
    if len(result) == 2:
        user, domain = result[0], result[1]
        return user, domain
    else:
        return None, None