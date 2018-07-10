import falcon
import json
import os
import io
import uuid

from PIL import Image

from settings import (MEADIA_FOLDER, thumb_folder, pic_folder)

from models.media import Media


class UploadMedia:

    def __init__(self):
        self.THUMBNAIL_SIZE = 320, 320
        self.THUMBNAIL_BOX = 0,0, 320, 320
        self.sizes = {
            'square': (1080, 1080),
            'landscape': (1920, 1080),
            'portrait': (1080, 1350),
            'thumbnail': (320, 320)
        }

    def create_image(self, bytes, filename):

        thumb = os.path.join(MEADIA_FOLDER, thumb_folder, filename + '.thumbnail')
        file_path = os.path.join(MEADIA_FOLDER, pic_folder, filename + '.jpeg')

        im = Image.open(bytes)
        im.save(file_path,'JPEG', quality=80, optimize=True, progressive=True)

        im.crop(self.THUMBNAIL_BOX)
        im.thumbnail(self.THUMBNAIL_SIZE, Image.ANTIALIAS)
        im.save(thumb, "jpeg")

        return im.size[0], im.size[1], "Image"

    def on_post(self, req, resp):

        image = req.get_param('file')

        if image == None:
            raise falcon.HTTPMissingParam('file')

        # Get a free id for the image
        valid = False
        identity = ""
        while not valid:
            ident = str(uuid.uuid4())
            valid = not Media.select().where(Media.media_name == identity).exists()
        
        #Send task to create image object
        width, height, mtype = self.create_image(io.BytesIO(image.file.read()), ident)

        description = req.get_param('description') or ""
        focus_x = 0
        focus_y = 0

        if req.get_param('focus'):
            focus_x, focus_y = req.get_param('focus').split(',')

        m = Media.create(
            media_name = ident,
            height = height,
            width = width,
            focus_x = focus_x,
            focus_y = focus_y,
            media_type = mtype,
            description = description,
        )

        resp.body = json.dumps(m.to_json())
        resp.status = falcon.HTTP_200