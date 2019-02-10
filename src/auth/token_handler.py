import tornado

from models.token import Token
from api.v1.base_handler import BaseHandler, CustomError

class TokenAuthHandler(BaseHandler):
    """ Token based authentication for handlers """

    async def prepare(self):
        self.current_user = None
        auth = self.request.headers.get('Authorization')

        if auth:
            parts = auth.split()

            if parts[0].lower() != 'bearer':
                raise CustomError(reason="Invalid header authorization", status_code=401)
            elif len(parts) == 1:
                raise CustomError(reason="Invalid header authorization", status_code=401)
            elif len(parts) > 2:
                raise CustomError(reason="Invalid header authorization", status_code=401)

            token = parts[1]

            try:
                canditate = await self.application.objects.get(Token, key=token)
                self.current_user = canditate.user
            except Token.DoesNotExist:
                raise CustomError(reason="Invalid token", status_code=401)



    def get_login_url(self):
        return '/login'