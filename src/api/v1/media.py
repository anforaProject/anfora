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

from api.v1.base_handler import BaseHandler, CustomError

from auth.token_auth import (bearerAuth, is_authenticated, token_authenticated)
from auth.token_handler import TokenAuthHandler
from decorators.get_by_id import retrive_by_id

from managers.user_manager import UserManager

from tasks.media import store_media
from urls import (URIs, uri)

class UploadMedia(TokenAuthHandler):
        
    @token_authenticated
    async def post(self):

        user = self.current_user
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

        valid = manager.is_valid()

        if valid:
            description = self.get_argument('description', '')
            focus = (0,0)
            if self.get_argument('focus', False):
                args = self.get_argument('focus').replace(" ", "").split(',')
                if len(args) == 2:
                    focus = args[:2]

            extension = manager.get_media_type()
            
            urls = URIs(
                media=uri("media", {"id":ident, "extension": extension}),
                preview=uri("preview", {"id":ident, "extension": extension})
            )
            m = {
                "description": description,
                "id": ident, 
                "type": "unknown",
                "url": urls.media,
                "preview_url": urls.preview,
                "meta": None
            }   
            store_media(manager, ident, description, focus)

            self.write(json.dumps(m, default=str))
            self.set_status(200)
        else:
            raise CustomError(reason="Error storing files", status_code=400)
