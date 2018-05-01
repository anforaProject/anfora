import falcon
from falcon_auth import BasicAuthBackend

from models.followers import FollowerRelation
from models.user import User

class serverInfo(object):

    auth = {'auth_disabled': True}

    def get(self, req, rest):
        nUsers = User.select().count()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"users": nUsers})
