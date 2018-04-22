import json
import requests

from .errors import ASTypeError

class Object(object):
    attributes = ["type", "id", "name", "to"]
    type = "Object"

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

class Collection(Object):

    attributes = Object.attributes + ["items", "totalItems"]
    type = "Collection"

    def __init__(self, iterable=None, **kwargs):
        self.items = []

        Object.__init__(self, **kwargs)
        if iterable is None:
            return

        self.items = iterable

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, iterable):
        for item in iterable:
            if isinstance(item, Object):
                self._items.append(item)
            elif getattr(item, "to_activitystream", None):
                item = as_activitystream(item.to_activitystream())
                self._items.append(item)
            else:
                raise Exception("Invalid Activity object: {item}".format(item=item))

    def to_json(self, **kwargs):
        json = Object.to_json(self, **kwargs)
        items = [item.to_json() if isinstance(item, Object) else item for item in self.items]

        json.update({"items":items})
        return json

class OrderedCollection(Collection):
    attributes = Object.attributes + ["orderedItems", "totalItems"]
    type = "OrderedCollection"

    @property
    def totalItems(self):
        return len(self.items)
    @totalItems.setter
    def totalItems(self, value):
        pass

    @property
    def orderedItems(self):
        return self.items

    @orderedItems.setter
    def orderedItems(self, iterable):
        self.items = iterable

    def to_json(self, **kwargs):
        json = Collection.to_json(self, **kwargs)
        json["orderedItems"] = json["items"]
        del json["items"]
        return json


ALLOWED_TYPES = {

    "Object": Object,
    "Actor": Actor,
    "Person": Person,
    "Note": Note,
    "Collection": Collection,
    "OrderedCollection": OrderedCollection
}

def as_activitystream(obj):
    type = obj.get("type")

    if not type:
        msg = "Invalid ActivityStream object, the type is missing"
        raise errors.ASDecodeError(msg)

    if type in ALLOWED_TYPES:
        return ALLOWED_TYPES[type](**obj)

    raise errors.ASDecodeError("Invalid Type {0}".format(type))

def encode_activitystream(obj):
    if isinstance(obj, Object):
        return obj.to_json()

    raise ASTypeError("Unknown ActivityStream Type")
