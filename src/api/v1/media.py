import json
import logging
import os
import io
import uuid
from PIL import Image

from tornado.web import HTTPError, RequestHandler

from settings import (MEDIA_FOLDER, thumb_folder, pic_folder)

from models.media import Media
from managers.media_manager import MediaManager

from api.v1.base_handler import BaseHandler

from auth.token_auth import (bearerAuth, is_authenticated)
from decorators.get_by_id import retrive_by_id

from managers.user_manager import UserManager

from tasks.redis.spreadStatus import spread_status


logger = logging.getLogger(__name__)

class UploadMedia(BaseHandler):
        
    @bearerAuth
    async def post(self, user):
        
        if not 'file' in self.request.files.keys():
            self.write({"Error": "File not provided"})
            self.set_status(422)
            return
            
        image = self.request.files['file'][0]

        # Search for a valid id 
        valid = False
        ident = ""
        while not valid:

            try:
                ident = str(uuid.uuid4())
                media = await self.application.objects.get(Media, media_name = ident)
            except Media.DoesNotExist:
                valid = True # If we are here that means that the object exits


        manager = MediaManager(self.request.files['file'][0]['body'])

        if manager.is_valid():

            width, height, mtype = manager.store_media(ident)

            if width:

                description = self.get_argument('description', '')
                focus_x = 0
                focus_y = 0

                if self.get_argument('focus', False):
                    args = self.get_argument('focus').replace(" ", "").split(',')
                    if len(args) == 2:
                        focus_x, focus_y = args[:2]

                data = {
                    'media_name': ident,
                    'height': height,
                    'width': width,
                    'focus_x': focus_x,
                    'focus_y': focus_y,
                    'media_type': mtype,
                    'description': description
                }

                m = await self.application.objects.create(Media, **data)

                self.write(json.dumps(m.to_json(), default=str))
        else:
            self.write({"Error": "Error storing files"})
            self.set_status(500)
