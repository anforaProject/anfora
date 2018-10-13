import sys
import six

from models.user import User 
from models.token import Token

import peewee_async
import functools
from models.base import db

def retrive_by_id(model):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            #id is one of the arguments of the function
            try:
                obj = await self.application.objects.get(model, id=int(kwargs['pid']))
                kwargs["target"] = obj
                
            except model.DoesNotExist:
                print(e)
                self.set_status(404)
                self.write({"Error": "Object not found"})
                self.finish()
                return None

            return func(self, *args, **kwargs)
        return wrapper
    return decorator