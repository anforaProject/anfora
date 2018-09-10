import datetime
from peewee import *
from models.base import BaseModel
from models.user import UserProfile

topics = ('spam', 'content', 'harrasment')

class Report(BaseModel):

    target = ForeignKeyField(UserProfile)
    reporter = ForeignKeyField(UserProfile)
    message = TextField()
    reason = CharField(max_length=64)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_closed = BooleanField(default=False)

    def json(self):
        
        return {
            'target': self.target.json(),
            'reporter': self.reporter.json(),
            'message': self.message,
            'reason': self.reason,
            'created_at': self.created_at,
            'is_closed': self.is_closed
        }