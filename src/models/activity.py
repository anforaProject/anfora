from datetime import datetime
import json

from peewee import *

from models.user import UserProfile
from models.base import BaseModel

from urls import (URIs, uri)

class Activity(BaseModel):
    payload = TextField()
    created_at = DateTimeField(default = datetime.now)
    person = ForeignKeyField(UserProfile, backref='activities', on_delete='CASCADE')
    remote = BooleanField(default=False)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("activity", {"username": self.person.username,"id": self.id})
        return URIs(id=ap_id)

    def to_activitystream(self):
        payload = self.payload
        data = json.loads(payload)
        data.update({
            "id": self.uris.id
        })
        return data["object"]
