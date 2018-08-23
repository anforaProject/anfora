import datetime
import uuid
import binascii
import os

from peewee import *
from playhouse.shortcuts import model_to_dict

from models.base import BaseModel
from models.user import UserProfile

class Token(BaseModel):

    key = CharField(primary_key=True)
    user = ForeignKeyField(UserProfile, on_delete='CASCADE')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()
        
