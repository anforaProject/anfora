import redis
import os
import json

from models.status import Status
from models.media import Media
from models.user import UserProfile
from models.notification import Notification, notification_types

from tasks.config import huey
from managers.media_manager import MediaManager

@huey.task()
def store_media(manager, ident, description, focus):

    #Send task to create image object
    width, height, mtype = manager.store_media(ident)

    if width:
        description = description or ""
        focus_x = 0
        focus_y = 0

        if focus:
            focus_x, focus_y = focus.split(',')

        m = Media.create(
            media_name = ident,
            height = height,
            width = width,
            focus_x = focus_x,
            focus_y = focus_y,
            media_type = mtype,
            description = description,
        )