import json
import logging
import bcrypt
from email.utils import parseaddr

from tornado.web import HTTPError, RequestHandler

from models.user import UserProfile, User
from models.status import Status
from models.token import Token

from api.v1.base_handler import BaseHandler, CustomError
from auth.token_auth import bearerAuth, userPassLogin, basicAuth

from utils.atomFeed import generate_feed

from managers.user_manager import new_user_async, UserManager
from managers.notification_manager import NotificationManager
from tasks.emails import confirm_token

from settings import salt_code

from tasks.emails import send_password_reset
from tasks.timelines import *

from database import DATABASE

log = logging.getLogger(__name__)


class RedirectUsername(BaseHandler):

    async def get(self, username:str):
        
        try:
            user = await self.application.objects.get(UserProfile.select().join(User).where(User.username==username.lower()))

            self.redirect(f'/accounts/{user.id}')
        except:
            self.redirect('/404')


class AuthUser(BaseHandler):

    @basicAuth
    async def get(self, user):

        if user.is_remote:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Remote user"})

        token = Token.create(user=user)

        payload = {
            "token": "Bearer " + token.key
        }

        self.write(payload)
        self.set_status(200)


class UserHandler(BaseHandler):
    async def get(self, id):
        try:
            #person = await self.application.objects.get(User, User.id==int(id))
            profile = await self.application.objects.get(UserProfile, UserProfile.id==int(id))

            self.write(json.dumps(profile.to_json(), default=str).encode('utf-8'))
            self.set_status(200)
        except User.DoesNotExist:
            raise CustomError(reason="User not found", status_code=401)

class VerifyCredentials(BaseHandler):

    @bearerAuth
    async def get(self, user):

        self.write(json.dumps(user.to_json(), default=str).encode('utf-8'))

class ProfileManager(BaseHandler):

    """
    
        Update the profile info for an user.

        patch: Valid arguments are:

            - display_name: The name to show
            - note: A description
            - locked: true if the account is private
            - bot: true if the account is a bot
            - avatar: a file containing the image for the user account

    """

    @bearerAuth
    async def patch(self, user):

        errors = []

        valids_types = ['image/png', 'image/jpeg']

        if self.get_argument('display_name', None):
            if len(self.get_argument('display_name')) <= 31: 
                user.name = self.get_argument('display_name')
            else:
                errors.append('display_name length exceeded.')
        
        if self.get_argument('note', False):
            if len(self.get_argument('note')) <= 160:
                user.description = self.get_argument('note')
            else:
                errors.append('Note length exceeded.')

        if self.get_argument('locked', False):
            user.private = self.get_argument('locked') in ['true']

        if self.get_argument('bot', False):
            user.bot = self.get_argument('bot') in ['true']

        if 'avatar' in self.request.files.keys():
            if self.request.files['avatar'][0]['content_type'] in valids_types:
            # TO DO 
            # Review that this works
                user.avatar_file = user.update_avatar(self.request.files['avatar'][0]['body'])

        
        # Once all the changes have been made

        await self.application.objects.update(user)
        self.write(json.dumps(user.to_json(), default=str).encode('utf-8'))
    

class LogoutUser(BaseHandler):

    """
        Delete the token associated to an account.
        Therefor this ends its session.
    """

    @bearerAuth
    async def post(sef, user):
        token = self.request.headers.get('Authorization').split()[1]

        try:
            token = await self.application.objects.get(Token, key=token)

            if user == token.user:
                await self.application.objects.delete(token)
                self.write({"Success": "Removed token"})
            else:
                raise CustomError(reason="Unauthorized user", status_code=401)
        
        except Token.DoesNotExist:
            raise CustomError(reason="Token not valid", status_code=401)

class atomFeed(BaseHandler):

    async def get(self, id):

        try:
            user = await self.application.objects.get(User, id=id)
            if self.get_argument('max_id', False):
                feed = generate_feed(user, int(self.get_argument('max_id')))
            else:
                feed = generate_feed(user)
            
            self.set_header('Content-Type', 'application/xml')
            self.write(feed)  

        except User.DoesNotExist:
            raise CustomError(reason="User not available", status_code=404)

class UserURLConfirmation(BaseHandler):

    async def get(self, token):
        email = confirm_token(token)
        if email:
            try:
                user = self.application.objects.get(User, email=email)
                user.confirmed = True 
                self.application.objects.update(user)
            
            except User.DoesNotExist:
                raise CustomError(reason="User not available", status_code=404)
        else:
            raise CustomError(reason="Invalid code or too old", status_code=400)


class RegisterUser(BaseHandler):

    async def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        confirmation = self.get_argument('password_confirmation')
        email = self.get_argument('email')
        
        valid_password = password == confirmation

        if '@' not in parseaddr(email)[1]: 
            raise CustomError(reason="Invalid email", status_code=400)

        if valid_password:

            try:
                log.debug("Creating new user")
                profile = await new_user_async(
                    username = username, 
                    password = password,
                    email = parseaddr(email)[1]
                )

                if not profile:
                    log.error("Error creating profile")
                    self.set_status(402)
                    CustomError(reason="Wrong username. Valid characters are number, ascii letters and (.) (_)", status_code=400)
                else:
                    self.set_status(200)
                    self.write(json.dumps(profile.to_json(), default=str))

            except Exception as e:
                log.error(e)
                CustomError(reason="Error creating new user", status_code=500)
        
        else:
            raise CustomError(reason="User not available or password not matching", status_code=400)

class PasswordRecovery(BaseHandler):

    async def post(self):
        token = self.get_argument('token')
        data = confirm_token(token)
        if data:
            typ, email = data 
        else:
            self.write({"Error": "Code expired"})
            self.set_status(500)
            self.finish()
            return 
        
        if email:
            try:
                user = await self.application.objects.get(User, email=email)
                password = self.get_argument('password')
                confirmation = self.get_argument('password_confirmation')
                valid_password = password == confirmation

                if valid_password:
                    user.password = bcrypt.hashpw(password, salt_code) 
                    await self.application.objects.update(user)
                else:
                    raise CustomError(reason="Password and confirmation do not match", status_code=401)
            
            except User.DoesNotExist:
                raise CustomError(reason="User not found", status_code=404)
        else:
            raise CustomError(reason="Invalid code or too old", status_code=401)

class RequestPasswordRecovery(BaseHandler):

    async def post(self, email):
        try:
            user = await self.application.objects.get(User, email=email)
            profile = user.profile.get()
            send_password_reset(profile)
        except User.DoesNotExist:
            raise CustomError(reason="User not found", status_code=404)
        self.write({"Success": "If the email is our database we'll contact the user"})
        self.set_status(200)


class FollowUser(BaseHandler):

    @bearerAuth
    async def post(self, target_id, user):

        try:
            target = await self.application.objects.get(UserProfile, id=target_id)
            user.follow(target)
            add_to_timeline(user, target)
            NotificationManager(user).create_follow_notification(target)
            log.debug(f"{user.username} followed {target.username}")
        except User.DoesNotExist:
            raise CustomError(reason="User not found", status_code=404)

class UnFollowUser(BaseHandler):

    @bearerAuth
    async def post(self, target_id, user):

        try:
            target = await self.application.objects.get(UserProfile, id=target_id)
            user.unfollow(target)
            remove_from_timeline(user, target)
        except User.DoesNotExist:
            raise CustomError(reason="User not found", status_code=404)

class FetchFollowers(BaseHandler):

    async def get(self, id):
        try:
            user = await self.application.objects.get(UserProfile, id=id)
            followers = [follower.to_json() for follower in user.followers()]
            self.write(json.dumps(followers, default=str))
            self.set_status(200)
        except UserProfile.DoesNotExist:
            raise CustomError(reason="User not found", status_code=404)
            
class FetchFollowing(BaseHandler):

    async def get(self, id):
        try:
            user = await self.application.objects.get(UserProfile, id=id)
            followers = [following.to_json() for following in user.following()]
            self.write(json.dumps(followers, default=str))
            self.set_status(200)
        except UserProfile.DoesNotExist:
            raise CustomError(reason="User not found", status_code=404)
        except Exception as e:
            raise CustomError(reason="Unexpected error", status_code=500)
            log.error(e)
class Relationship(BaseHandler):



    @bearerAuth
    async def get(self, user):
        target_id = self.get_argument('id', None)

        if target_id:
            try:
                target = await self.application.objects.get(UserProfile, id=target_id)
                data = {
                    'id': target_id,
                }
                
                # Check if the current user is following that account

                manager = UserManager(user)
                target_manager = UserManager(target)

                data['following'] = await manager.is_following_async(self.application.objects, target)
                data['followed_by'] = await target_manager.is_following_async(self.application.objects, user)

                self.write(data)
                self.set_status(200)
            except UserProfile.DoesNotExist:
                log.error(f'User with id {target_id} not found')
                self.write({"Error": "Target user not found"})
                self.set_status(404)
        else:
            raise CustomError(reason="Targed it not provided", status_code=400)
            log.error("Missing target id on request")