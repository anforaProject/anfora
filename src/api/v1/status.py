import json
import logging

from tornado.web import HTTPError, RequestHandler

from models.user import UserProfile, User
from models.status import Status
from models.token import Token
from models.media import Media 

from api.v1.base_handler import BaseHandler

from auth.token_auth import (bearerAuth, is_authenticated)
from decorators.get_by_id import retrive_by_id

from managers.user_manager import UserManager

from tasks.redis.spreadStatus import spread_status
from tasks.redis.remove_status import remove_status


logger = logging.getLogger(__name__)


class StatusHandler(BaseHandler):
    """
    Operate over the status with a given id.
    
    The delete operation requires the token to auth the user

    """

    @retrive_by_id(Status)
    def get(self, pid, target):
        self.write(json.dumps(target.to_json(), default=str))
            
    @bearerAuth
    @retrive_by_id(Status)
    def delete(self, pid, user, target):
        if target.user.id == user.id:
            remove_status(target)
        else:
            self.write({"Error": "You can't perform this action"})
            self.set_status(401)


class FavouriteStatus(BaseHandler):

    @bearerAuth
    @retrive_by_id(Status)
    def post(self, pid, target, user):
        UserManager(user).like(target)
        self.write(json.dumps(target, default=str))

class UnFavouriteStatus(BaseHandler):
    
    @bearerAuth
    @retrive_by_id(Status)
    def post(self, pid, target, user):

        UserManager(user).dislike(target)
        self.write(json.dumps(target, default=str))

class FetchUserStatuses(BaseHandler):
    async def get(self, id):
        try:
            photos = await self.application.objects.execute(
                Status.select().join(UserProfile).where(Status.user.id == id).order_by(Status.created_at.desc())
            )
            
            query = [photo.to_json() for photo in photos]
            self.write(json.dumps(query, default=str))
        except User.DoesNotExist:
            self.write({"Error": "User not found"})
    

class UserStatuses(BaseHandler):

    """
    Do stuff related to the status of one user

    get: requires the id argument
    """
    @bearerAuth
    async def get(self, user):
        photos = await self.application.objects.execute(
            Status.select().where(Status.user == user).order_by(Status.created_at.desc())
        )
        
        query = [photo.to_json() for photo in photos]
        self.write(json.dumps(query, default=str))
    
    @bearerAuth
    async def post(self, user):
        if self.get_argument('media_ids', False):
            data = {
                "caption": self.get_argument('status', ''),
                "visibility": bool(self.get_argument('visibility', False)),
                "user": user,
                "sensitive": bool(self.get_argument('sensitive', False)),
                "remote": False,
                "sotory": bool(self.get_argument('story', False))
            }
            
            if data['sensitive']:
                data['spoliet_text'] = self.get_argument('spoiler_text', '')

            status = await self.application.objects.create(Status, **data)

            
        
            for image in self.get_argument('media_ids').split(","):
                try:
                    m = await self.application.objects.get(Media, media_name=image)
                    m.status = status
                    await self.application.objects.update(m)
                except Media.DoesNotExist:
                    logger.error(f"Media id not found {image} for {status.id}")

            await self.application.objects.execute(
                UserProfile.update({UserProfile.statuses_count: UserProfile.statuses_count + 1}).where(UserProfile.id == user.id)
            )
            spread_status(status)

            self.write(json.dumps(status.to_json(),default=str))

        elif self.get_argument('in_reply_to_id', False):

            try:
                replying_to = await self.application.objects.get(Status,id=int(self.get_argument('in_reply_to_id')))
            except Status.DoesNotExist:
                self.set_status(500)
                self.write({"Error": "Replying to bad ID"})

        else:

            self.set_status(500)
            self.write({"Error": "No media attached nor in reply to"})

