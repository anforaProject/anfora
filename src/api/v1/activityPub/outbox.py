import json
import os, sys, io
import uuid

from PIL import Image

from models.user import UserProfile, User
from models.status import Status
from models.followers import FollowerRelation
from models.activity import Activity

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import  store
from tasks.tasks import deliver
from tasks.tasks import create_image

from activityPub.identity_manager import ActivityPubId
from managers.timeline_manager import TimelineManager
from api.v1.base_handler import BaseHandler

from decorators.pagination import ap_pagination

class Outbox(BaseHandler):

    def get(self, username):
        user = User.get_or_none(username=username)
        pagination = ap_pagination(self)
        if user:
            user = user.profile.get()

            # Retrive statuses
            objects = []
            for k in TimelineManager(user).query():
                try:
                    objects.append(Status.get(Status.identifier == status).to_activitystream())
                except:
                    pass

            print(objects)
            # create collection page
            collectionPage = activities.OrderedCollectionPage(map(activities.Note, objects), **pagination)

            # create collection
            collection = activities.OrderedCollection([collectionPage])
            self.write(json.dumps(collectionPage.to_json(context=True)))
            self.set_status(200)

