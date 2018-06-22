import io
import sys

from models.photo import Photo
from models.user import User


def upload_image(user, message, description, ident
                    ,sensitive, dimensions, filename):

    return Photo.create(title=filename,
                         user=user,
                         message = message or '',
                         description = description or '',
                         sensitive = sensitive or '',
                         media_type="Image",
                         width = dimensions[0],
                         height=dimensions[1],
                         media_name=ident,
                         )
