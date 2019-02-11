import json
import logging
import datetime
import html 

from hashids import Hashids
from tornado.web import HTTPError, RequestHandler

from models.user import UserProfile, User
from models.status import Status
from models.token import Token
from models.media import Media 

from api.v1.base_handler import BaseHandler, CustomError

from auth.token_auth import (bearerAuth, is_authenticated, token_authenticated)
from auth.token_handler import TokenAuthHandler
from decorators.get_by_id import retrive_by_id
from decorators.lists import group_lists
from managers.user_manager import UserManager
from anfora_parser.parser import Parser

from tasks.redis.spreadStatus import spread_status
from tasks.redis.remove_status import remove_status
from tasks.media import atach_media_to_status

from settings import (salt_code, BASE_URL)

logger = logging.getLogger(__name__)


class StatusHandler(TokenAuthHandler):
    """
    Operate over the status with a given id.
    
    The delete operation requires the token to auth the user

    """

    @retrive_by_id(Status)
    def get(self, pid, target):
        self.write(json.dumps(target.to_json(), default=str))
            
    @token_authenticated
    @retrive_by_id(Status)
    def delete(self, pid, target):
        user = self.current_user
        if target.user.id == user.id:
            remove_status(target)
        else:
            self.write({"Error": "You can't perform this action"})
            self.set_status(401)


class FavouriteStatus(TokenAuthHandler):

    @token_authenticated
    @retrive_by_id(Status)
    def post(self, pid, target):
        UserManager(self.current_user).like(target)
        self.write(json.dumps(target, default=str))

class UnFavouriteStatus(TokenAuthHandler):
    
    @token_authenticated
    @retrive_by_id(Status)
    def post(self, pid, target):
        UserManager(self.current_user).dislike(target)
        self.write(json.dumps(target, default=str))

class FetchUserStatuses(BaseHandler):
    async def get(self, id):
        try:
            photos = await self.application.objects.execute(
                Status.select().
                join(UserProfile).
                where((Status.user.id == id) & Status.in_reply_to_id.is_null())
                .order_by(Status.created_at.desc())
            )
            
            query = [photo.to_json() for photo in photos]
            self.write(json.dumps(query, default=str))
        except User.DoesNotExist:
            self.write({"Error": "User not found"})
  

class UserStatuses(TokenAuthHandler):

    """
    Do stuff related to the status of one user

    get: requires the id argument
    """
    @token_authenticated
    async def get(self, user):
        photos = await self.application.objects.execute(
            Status.select().where(Status.user == user).order_by(Status.created_at.desc())
        )
        
        query = [photo.to_json() for photo in photos]
        self.write(json.dumps(query, default=str))
    
    
    
    @token_authenticated
    @group_lists
    async def post(self, *args, **kwargs):
        """
        Handle creation of statuses
        """

        user = self.current_user
        print(user.username)
        hashids = Hashids(salt=salt_code, min_length=9)

        if self.kwargs.get('media_ids', False):
            data = {
                "caption": self.get_argument('status', ''),
                "visibility": bool(self.get_argument('visibility', False)),
                "user": user,
                "sensitive": bool(self.get_argument('sensitive', False)),
                "remote": False,
                "sotory": bool(self.get_argument('story', False)),
                "identifier": hashids.encode(int(str(user.id) + str(int(datetime.datetime.now().timestamp())))) # TODO: We're losing time here
            }
            
            if data['sensitive']:
                data['spoliet_text'] = self.get_argument('spoiler_text', '')

            par = Parser(domain=BASE_URL)
            parsed = par.parse(html.escape(data["caption"]))

            mentions = parsed.users 
            
            data['caption'] = parsed.html

            status = await self.application.objects.create(Status, **data)
        
            for image in self.kwargs.get('media_ids'):
                atach_media_to_status(status, image)

            await self.application.objects.execute(
                UserProfile.update({UserProfile.statuses_count: UserProfile.statuses_count + 1}).where(UserProfile.id == user.id)
            )

            spread_status(status, mentions)

            self.write(json.dumps(status.to_json(),default=str))

        elif self.get_argument('in_reply_to_id', False):

            try:
                replying_to = await self.application.objects.get(Status,identifier=self.get_argument('in_reply_to_id'))

                data = {
                    "caption": self.get_argument('status', ''),
                    "visibility": bool(self.get_argument('visibility', False)),
                    "user": user,
                    "sensitive": bool(self.get_argument('sensitive', False)),
                    "remote": False,
                    "identifier": hashids.encode(int(str(user.id) + str(int(datetime.datetime.now().timestamp())))),
                    "in_reply_to": replying_to
                }

                status = await self.application.objects.create(Status, **data)
                self.write(json.dumps(status.to_json(),default=str))

            except Status.DoesNotExist:
                raise CustomError(reason="Replying to bad ID", status_code=400)


        else:
            raise CustomError(reason="No media attached nor in reply to", status_code=400)

