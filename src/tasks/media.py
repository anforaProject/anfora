import os
import json
import logging
from typing import Tuple

import redis

from models.status import Status
from models.media import Media
from models.user import UserProfile
from models.notification import Notification, notification_types

from tasks.config import huey
from managers.media_manager import MediaManager

logger = logging.getLogger(__name__)


@huey.task()
def store_media(manager: MediaManager, ident: str, description: str, focus:Tuple[int, int]) -> None:

    #Send task to create image object
    width, height, mtype = manager.store_media(ident)

    if width:
        description = description or ""
        focus_x = 0
        focus_y = 0

        if focus:
            focus_x, focus_y = focus

        m = Media.create(
            media_name = ident,
            height = height,
            width = width,
            focus_x = focus_x,
            focus_y = focus_y,
            media_type = mtype,
            description = description,
        )

@huey.task()
def atach_media_to_status(status, media_id):
    try:
        m = Media.get(Media.media_name==media_id)
        m.status = status
        m.save()
    except Media.DoesNotExist:
        logger.error(f"Media id not found {image} for {status.id}")