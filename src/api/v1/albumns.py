import json
import re 

from api.v1.base_handler import BaseHandler
from auth.token_auth import (bearerAuth, is_authenticated)
from settings import (MEDIA_FOLDER, salt_code)

from models.album import Album
logger = logging.getLogger(__name__)

class AlbumHandler(BaseHandler):

    """
    Handle all the stuff related to Albums

    post - Create a new Album
    update - Update status related to albums
    delete - delete the album
    """

    @bearerAuth
    async def post(self, user):
        data = {
            'name': self.get_argument('name', 'New album' ),
            'public': self.get_argument('public', False),
            'user': user,
            'description': self.get_argument('description', 'No caption provided')
        }

        try:
            album = await self.application.objects.create(Album, **data)
            self.set_status(200)
            self.write(json.dumps(album.to_json(), default=str))
        except:
            self.set_status(500)
            self.write({"Error": "Error crating album"})
            logger.error("Error creating album")

    @retrive_by_id(Album)
    @bearerAuth
    async def update(self, pid, target, user):
        
        # Check if the user is the owner of the album
        if target.user.id == user.id:
            # Retrive a list of ids of status to add 
            for self.request.arguments:


        else:
            self.set_status(401)        
