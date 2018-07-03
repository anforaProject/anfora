import re

def extractUser(uri):

    result = uri.split("@")
    if len(result) == 2:
        user, domain = result[0], result[1]
        return user, domain
