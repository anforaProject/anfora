import io
import sys

from models.status import Status
from models.user import User


def upload_image(user, message, description, ident
                    ,sensitive, dimensions, filename):

    return Status.create(title=filename,
                         user=user,
                         message = message or '',
                         description = description or '',
                         sensitive = sensitive or '',
                         width = dimensions[0],
                         height=dimensions[1],
                         media_name=ident,
                         )
