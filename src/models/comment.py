import datetime

from peewee import (ForeignKeyField, DateTimeField,CharField)

from models.status import Status
from models.base import BaseModel
from models.hashtags import Hashtag
from models.user import UserProfile

class Comment(BaseModel):

    status = ForeignKeyField(Status, backref="comments")
    user = ForeignKeyField(UserProfile, backref="comments")    
    created_at = DateTimeField(default=datetime.datetime.now)
    ap_id = CharField(max_length=60)
    
