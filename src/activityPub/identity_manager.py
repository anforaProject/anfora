import json
import requests
from urllib.parse import urlparse

from settings import DOMAIN

#ActivityPub
from activityPub.activities import as_activitystream

#Models
from models.user import UserProfile, User
from managers.user_manager import new_user
from models.followers import FollowerRelation

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
        Returns an instance of Person
        """


        #Mastodon needs this header
        headers = {'Accept': 'application/activity+json'}

        #Make a request to the server
        res = requests.get(self.uri, headers=headers)

        if res.status_code != 200:
            raise Exception("Failed to dereference {0}".format(self.uri))

        return as_activitystream(res.json())

    def get_or_create_remote_user(self):
        """ 
            Returns an instance of User after looking for it using it's ap_id
        """
        user = UserProfile.get_or_none(ap_id=self.uri)
        if not user:
            user = self.dereference()
            hostname = urlparse(user.id).hostname
            username = "{0}@{1}".format(user.preferredUsername, hostname)
            user = new_user(
                username=user.preferredUsername,
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
        return user

    def _local_uri(self, uri):
        host = urlparse(uri).hostname

        return uri == DOMAIN
        

    def uri_to_resource(self, klass):

        if self._local_uri(self.uri):
            if klass.__name__ == 'User':
                return UserProfile.get_or_none(ap_id=self.uri)
        else:
            return self.get_or_create_remote_user()

        