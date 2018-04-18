from activityPub.activities.objects import (ALLOWED_TYPES, Object, Actor,
                                            Person, Note)

from activityPub.activities import errors

class Activity(Object):
    attributes = Object.attributes + ["actor", "object"]
    type = "Activity"

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
