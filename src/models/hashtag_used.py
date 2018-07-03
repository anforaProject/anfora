import datetime

from peewee import (ForeignKeyField, CharField)

from models.photo import Photo
from models.base import BaseModel
from models.hashtags import Hashtag
from models.comment import Comment

class HashtagUsed(BaseModel):

    """
    This class represents a relation between hashtags and posts or comments.
    This way one can reference both hashtags and search in both types of content
    """

    photo = ForeignKeyField(Photo, null=True, backref="hashtags")
    comment = ForeignKeyField(Comment, null=True, backref="hashtags")
    hastag = ForeignKeyField(Hashtag)
