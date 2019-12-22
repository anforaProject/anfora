import datetime
import uuid
import binascii
import os
import io
import logging

from tortoise.models import Model
from tortoise import fields

from urls import (uri, URIs)
from utils import load_config

from media_api import fetch_media_as_by_id, fetch_media_by_id
from user_api import fetch_user_by_username
from comment_api import fetch_comments_by_id

config = load_config()

MEDIA_FOLDER = config['media_folder']

log = logging.getLogger(__name__)

class Status(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add = True)
    updated_at = fields.DatetimeField(auto_now = True)
    caption = fields.CharField(512, default="")
    spoiler_text = fields.CharField(128, default="")
    is_public = fields.BooleanField(default=True)
    user = fields.ForeignKeyField('models.UserProfile', related_name="user", on_delete="CASCADE")
    sensitive = fields.BooleanField(default=False)
    remote = fields.BooleanField(default=False)
    ap_id = fields.CharField(512, default="")
    in_reply_to = fields.ForeignKeyField('models.Status', related_name="reply_to")
    favourites_count = fields.IntField(default=0)
    reblog_count = fields.IntField(default=0)
    ident = fields.CharField(null=False, unique=True, max_length=32)
    media_files = fields.ManyToManyField('models.Status',
                                    related_name = 'status'
    )
    def __repr__(self):
        return self.ident

    async def to_activitystream(self):
        await self.fetch_related('user')
        media_files = await fetch_media_as_by_id(self.ident)
        
        data = {
            "id": uri("status", {"username":self.user.username, "id":self.id}),
            "type": "Note",
            "summary": None,
            
            "published": self.created_at.replace(microsecond=0).isoformat() + "Z",
            "url": self.uris.url,
            "attributedTo": await self.user.ap_id,
            #"hashtags": self.hashtags,
            "sensitive": self.sensitive,
            "attachment": media_files,
            "spoiler_text": self.spoiler_text,
            "content": self.caption,
        }

        if self.is_public:
            data['to'] = ["https://www.w3.org/ns/activitystreams#Public"]
        else:
            data['to'] = []
        
        data['cc'] = [self.user.uris.followers] 

        return data

    async def to_json(self):
        await self.fetch_related('user')
        media_files = await fetch_media_by_id(self.ident)
        comments = await fetch_comments_by_id(self.ident)
        user = await fetch_user_by_username(self.user.username)
        
        data = {
            "id": self.identifier,
            "description": self.caption,
            "message": self.caption,
            "hashtags": self.hashtags,
            "likes": self.favourites_count,
            "account": user,
            "sensitive": self.sensitive,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            "media_attachments": media_files,
            "comments": comments

        }

        return data



class UserProfile(Model):

    id = fields.BigIntField(pk=True)
    username = fields.CharField(64, unique=True, null=True)

    def __repr__(self):
        return self.username

class Media(Model):
    id = fields.BigIntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add = True)
