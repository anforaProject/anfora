import json
import os
import requests
import logging
from urllib.parse import urlparse
from typing import (Any)
from settings import DOMAIN

#ActivityPub
from activityPub.activities import as_activitystream

#Models
from models.user import UserProfile, User
from models.followers import FollowerRelation

# from managers.user_manager import new_user TODO: FIX THIS


class IdentityManager:

    def __init__(self, identity):
        if "#" in identity:
            self.uri = identity.split("#")[0]
        else:
            self.uri = identity
        

class ActivityPubId(IdentityManager):

    def dereference(self):

        """
        Get user info from remote server.
        Returns an instance of dict (activity stream object)
        """


        #Mastodon needs this header
        headers = {'Accept': 'application/activity+json'}

        #Make a request to the server
        res = requests.get(self.uri, headers=headers, verify=False)

        if res.status_code != 200:
            raise Exception("Failed to dereference {0}".format(self.uri))

        return as_activitystream(res.json())

    def get_or_create_remote_user(self) -> UserProfile:
        """ 
            Returns an instance of User after looking for it using it's ap_id
        """
        logging.debug(self.uri)
        user = UserProfile.get_or_none(ap_id=self.uri)
        if user == None:
            user = self.dereference()
            hostname = urlparse(user.id).hostname
            #username = "{0}@{1}".format(user.preferredUsername, hostname)
            logging.debug(f"I'm going to request the creation of user with username @{user.preferredUsername}")

            username = f'{user.preferredUsername}@{hostname}'

            user = new_user(
                username=username,
                name=user.name,
                ap_id=user.id,
                is_remote=True,
                email = None,
                password = "what",
                description=user.summary,
                is_private=user.manuallyApprovesFollowers,
                public_key=user.publicKey['publicKeyPem']
            )
        #print(user)
        logging.debug(f"remote user: {user}")
        return user

    def _local_uri(self, uri):
        host = urlparse(uri).hostname

        return uri == DOMAIN
        

    def uri_to_resource(self, klass) -> Any:

        if self._local_uri(self.uri):
            if klass.__name__ == 'User':
                return UserProfile.get_or_none(ap_id=self.uri)
        else:
            return self.get_or_create_remote_user()

        