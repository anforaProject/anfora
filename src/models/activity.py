from datetime import datetime

from peewee import *

from models.user import User
from models.base import BaseModel

from activityPub.helpers import (URIs, uri)

class Activity(BaseModel):
    ap_id = CharField()
    payload = TextField()
    created_at = DateTimeField(default = datetime.now)
    person = ForeignKey(User, backref='activities')
    remote = BooleanField(default=False)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("activity", self.person.username, self.id)
        return URIs(id=ap_id)

    def to_activitystream(self):
        payload = self.payload.decode("utf-8")
        data = json.loads(payload)
        data.update({
            "id": self.uris.id
        })
        return data
