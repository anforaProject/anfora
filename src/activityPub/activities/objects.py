import json
import requests

from .errors import ASTypeError

class Object(object):
    attributes = ["type", "id", "name", "to"]
    type = "Object"

    def __init__(self, obj=None, *args, **kwargs):
        if obj:
            self.__init__(**obj.to_activitystream())

        for key in self.attributes:
            if key == "type":
                continue

            value = kwargs.get(key)
            if isinstance(value, dict) and value.get("type"):
                value = as_activitystream(value)

            if value != None:
                print("Setting ", key, " to ", value)
                setattr(self, key, value)

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

            context_content = ["https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1"
            ]

            values["@context"] = context_content
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

class Note(Object):
    attributes = Object.attributes + ["message", "actor","description",
    "sensitive","likes", "created_at", "media_url", "preview_url"]
    type = "Note"

class Collection(Object):

    attributes = Object.attributes + ["items", "totalItems"]
    type = "Collection"

    def __init__(self, iterable=None, **kwargs):
        self._items = []
        Object.__init__(self, **kwargs)
        if iterable is None:
            return

        for item in iterable:
            if isinstance(item, Object):
                self._items.append(item.to_json())
            elif getattr(item, "to_activitystream", None):
                item = as_activitystream(item.to_activitystream())
                self._items.append(item)
            else:
                self._items.append(str(item))

    @property
    def items(self):
        return self._items

    @property
    def totalItems(self):
        return len(self.items)

    @items.setter
    def items(self, iterable):
        if iterable:
            for item in iterable:
                if isinstance(item, Object):

                    self._items.append(item.to_json())
                elif getattr(item, "to_activitystream", None):
                    item = as_activitystream(item.to_activitystream())
                    self._items.append(item)
                else:
                    raise Exception("Invalid Activity object: {item}".format(item=item))

    def to_json(self, **kwargs):
        json = Object.to_json(self, **kwargs)
        return json

class OrderedCollection(Collection):
    attributes = Object.attributes + ["first"]
    type = "OrderedCollection"


    @property
    def first(self):
        return self.items


    @first.setter
    def first(self, iterable):
        self.items = iterable

    def to_json(self, **kwargs):
        data = Collection.to_json(self, **kwargs)
        data["totalItems"] = self.totalItems
        return data

class OrderedCollectionPage(OrderedCollection):
    attributes = Object.attributes + ['partOf', 'next', 'id', 'orderedItems']
    type = "OrderedCollectionPage"

    @property
    def totalItems(self):
        if(self.items and self.items[0].type == 'OrderedCollection'):
            return self.items[0].totalItems()
        else:
            return len(self.items)

    @property
    def orderedItems(self):
        return self.items

    @orderedItems.setter
    def orderedItems(self, iterable):
        self.items = iterable


    def to_json(self, **kwargs):
        json = Object.to_json(self, **kwargs)
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
