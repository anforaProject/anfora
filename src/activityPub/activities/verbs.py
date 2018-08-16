from activityPub.activities.objects import (ALLOWED_TYPES, Object, Actor,
                                            Person, Note)

from copy import copy

from activityPub.activities import errors

from utils.username import extract_user
from models.follow_request import FollowRequest
from models.user import UserProfile

class Activity(Object):
    attributes = Object.attributes + ["actor", "object"]
    type = "Activity"

    def user_from_uri(uri):
        username, domain = extract_user(uri)
        user = UserProfile.get_or_none(username=username)
        return user

    def get_audience(self):

        audience = []

        for attr in ["to", "bto", "cc", "bcc", "audience"]:
            value = getattr(self, attr, None)
            if not value:
                continue

            if isinstance(value, str):
                audience.append(value)

        return set(audience)

    def strip_audience(self):
        new = copy(self)
        if getattr(new, "bto", None):
            delattr(new, "bto")
        if getattr(new, "bcc", None):
            delattr(new, "bcc")

        return new

    def validate(self):
        return

    def object_uri(self):
        return self.object

class Create(Activity):

    type = "Create"

    def validate(self):
        msg = None
        if not getattr(self, "actor", None):
            msg = "Invalid Create activity, actor is missing"
        elif not getattr(self, "object", None):
            msg = "Invalid Create activity, object is missing"
        elif not isinstance(self.actor, Actor) and not isinstance(self.actor, str):
            msg = "Invalid actor type, must be an Actor or a string"
        elif not isinstance(self.object, Object):
            msg = "Invalid object type, must be an Object"

        if msg:
            raise errors.ASValidateException(msg)

class Follow(Activity):
    type = "Follow"

class Reject(Activity):
    type = "Reject"

class Accept(Activity):
    type = "Accept"

class RsaSignature2017(Activity):
    type = "RsaSignature2017"

ALLOWED_TYPES.update({
    "Activity": Activity,
    "Create": Create,
    "Follow": Follow,
    "Accept": Accept,
    "Reject": Reject,
    "RsaSignature2017": RsaSignature2017
})
