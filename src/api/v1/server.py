import json
from tornado.web import HTTPError, RequestHandler

from settings import (ID, NODENAME, DOMAIN, SCHEME)
from release_info import VERSION

from models.followers import FollowerRelation
from models.user import UserProfile, User
from models.status import Status

from api.v1.base_handler import BaseHandler

from utils.username import extract_user
from utils.webfinger import Webfinger

class WellKnownNodeInfo(BaseHandler):

    def get(self):

        links = [
            {
                "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                "href": "{}/nodeinfo.json".format(ID),
            }
        ]

        self.write(links)


class NodeInfo(BaseHandler):

    async def get(self):

        number_of_users = await self.application.objects.count(UserProfile.select())
        number_of_statuses = await self.application.objects.count(Status.select())
        
        response = {
            "version": "2.0",
            "software": {
                "name": "Anfora",
                "version": "Anfora {}".format(VERSION),
            },
            "protocols": ["activitypub"],
            "services": {"inbound": [], "outbound": []},
            "openRegistrations": False,
            "usage": {
                "users": {
                    "total": number_of_users
                },
                "localPosts": number_of_statuses
            },
            "metadata": {
                "sourceCode": "https://github.com/anforaProject/anfora",
                "nodeName": NODENAME,
            },    
        }

        self.write(response)

class WellKnownWebFinger(BaseHandler):

    async def get(self):

        if not self.get_argument('resource', False):
            self.set_status(400)
            self.write({"Error": "No resource was provided"})

        resources = self.get_argument('resource')

        username, domain = extract_user(resources)

        if username == None and domain == None:
            self.write({"Error": "Bad resource provided"})
            return

        if domain == DOMAIN:
            try:
                user = await self.application.objects.get(User, username=username)

                profile = await self.application.objects.get(user.profile)
                response = Webfinger(profile).generate()
                self.write(response)
            except User.DoesNotExist:
                self.write({"Error": "User not found"})
                self.set_status(404)
        else:

            self.write({"Error": "Incorrect domain"})
            self.set_status(400)