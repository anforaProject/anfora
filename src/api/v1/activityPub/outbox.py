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

    async def get(self, username):
        user = User.get_or_none(username=username)
        pagination = ap_pagination(self)
        if user:
            user = user.profile.get()

            # Retrive statuses

            objects = await self.application.objects.execute(Status.select().where(Status.user == user ).order_by(Status.id).paginate(pagination['page'], pagination['default_pagination']))
            objects = map(lambda x: x.to_activitystream(), objects)
            # create collection page
            collectionPage = activities.OrderedCollectionPage(map(activities.Note, objects), **pagination)

            # create collection
            collection = activities.OrderedCollection([collectionPage])
            self.write(json.dumps(collectionPage.to_json(context=True)))
            self.set_status(200)

