import json
import .errors
import requests

class Object(object):
    attributes = ["type", "id", "name", "to"]
    type = Object

    def __init__(self, obj=None, **kwargs):
        if obj:
            self.__init__(**obj.to_activitystream())
        for key in self.attributes:
            if key == "type":
                continue

            value = kwargs.get(key)
            if value is None:
                continue

            if isinstance(value, dict) and value.get("type"):
                value = as_activitystream(value)
            self.__setattr__(key, value)

    def __str__(self):
        content = json.dumps(self, default=encode_activitystream)
        return "<{type}: {content}>".format(type=self.type,content=content)

    def to_json(self, context=False):
        values = {}
        for attribute in self.attributes:
            value = getattr(self, attribute, None)
            if value is None:
                continue
            if isinstance(value, Object):
                value = value.to_json()
            values[attribute] = value
        to = values.get("to")
        if isinstance(to, str):
            values["to"] = [to]
        elif getattr(to, "__iter__", None):
            values["to"] = []
            for item in to:
                if isinstance(item, str):
                    values["to"].append(item)
                if isinstance(item, Object):
                    values["to"].append(item.id)

        if context:
            values["@context"] = "https://www.w3.org/ns/activitystreams"

        return values

class Actor(Object):

    attributes = Object.attributes + [
        "target",
        "preferredUsername",
        "following",
        "followers",
        "outbox",
        "inbox",
    ]

    type="Actor"

    def send(self, activity):
        res = requests.post(self.inbox, json=activity.to_json(context=True))
        if res.status_code != 200:
            raise Exception

class Person(Actor):
    type = "Person"

class Note(object):
    attributes = Object.attributes + ["content", "actor"]
    type = "Note"

ALLOWED_TYPES = {

    "Object": Object,
    "Actor": Actor,
    "Person": Person,
    "Note": Note,
}
