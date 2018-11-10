import json
import os
import logging
import uuid
import io
import sys

from api.v1.base_handler import BaseHandler

from models.user import UserProfile
from models.notification import Notification
from tasks.redis.spreadStatus import spread_status
from tasks.tasks import create_image
from tasks.redis.remove_status import remove_status
from auth.token_auth import bearerAuth, userPassLogin, basicAuth

from managers.user_manager import UserManager


log = logging.getLogger(__name__)

class NotificationHandler(BaseHandler):

    @bearerAuth
    async def get(self, user: UserProfile) -> str:

        try:
            query = await self.application.objects.execute(
                Notification.select().where(Notification.target==user).order_by(Notification.created_at.desc()).limit(100)
            )
            if query:
                self.write(json.dumps([x.to_json() for x in query], default=str))
            else:
                self.write([])
        except Exception as e:
            log.error(str(e))

