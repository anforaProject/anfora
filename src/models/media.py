import json
import os

from tortoise.models import Model
from tortoise import fields

base_path = os.getenv("DOMAIN")
uploads = os.getenv("UPLOAD_FOLDER")


class Media(Model):

    mid = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("src.models.users.UserProfile", related_name="owner")
    description = fields.TextField()
    focusx = fields.DecimalField(max_digits=2, decimal_places=1)
    focusy = fields.DecimalField(max_digits=2, decimal_places=1)
    filter_name = fields.CharField(30, default="")
    created = fields.DatetimeField(auto_now_add=True)
    attached = fields.BooleanField(default=False)
    extension = fields.CharField(4)

    def to_json(self):
        data = {
            "filepath": f"{base_path}/{uploads}/{self.pk}",
            "description": self.description,
            "filter_name": self.filter_name,
            "focusx": self.focusx,
            "focusy": self.focusy,
            "created": self.created,
        }

        return json.dumps(data, default=str)
