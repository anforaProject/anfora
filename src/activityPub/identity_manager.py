import json
import requests

#ActivityPub
from activityPub.activities import as_activitystream

#Models
from models.user import User
from models.followers import FollowerRelation

class IdentityManager(object):

    def __init__(self, identity):
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
        user = User.get_or_none(ap_id=self.uri)
        if not user:
            user = dereference(self.uri)
            hostname = urlparse(user.id).hostname
            username = "{0}@{1}".format(user.preferredUsername, hostname)
            user = User.create(
                username=user.preferredUsername,
                name=user.name,
                ap_id=user.id,
                remote=True,
                password = "what",
                description=user.summary,
                private=user.manuallyApprovesFollowers,
                public_key="user.public_key.publicKeyPem"
            )
        #print(user)
        return user