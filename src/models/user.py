import datetime
import uuid
import binascii
import os

from peewee import *
from playhouse.shortcuts import model_to_dict

from models.base import BaseModel

class User(BaseModel):

    username = CharField(unique=True)
    password = CharField()
    admin = BooleanField(default=False)
    created_at =  DateTimeField(default=datetime.datetime.now)
    disabled = BooleanField(default=False)
    moderator = BooleanField(default=False)
    confirmed = BooleanField(default=False)
    email = CharField(unique=True)
    confirmation_sent_at = DateTimeField()
    last_sign_in_at = IntegerField()
    
