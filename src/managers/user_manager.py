import bcrypt
import re 
import logging
from typing import Union

from peewee_async import Manager

from settings import salt_code
from models.user import User, UserProfile
from tasks.emails import send_activation_email

from models.status import Status 
from models.like import Like

from tasks.redis.spreadStatus import like_status

from models.base import db
from urls import uri

class UserManager:

    def __init__(self, user):
        self.user = user 

    def like(self, status):
        """
            user: UserProfile - User liking the status

            Returns True if the action was successful
        """

        # Check if the user already liked it

        if Like.get_or_none(user=self.user,status=status):
            return False
        
        # First we create the like object
        Like.create(
            user = self.user,
            status = status,
        )

        # Update the counter in the object
        Status.update({Status.favourites_count: Status.favourites_count + 1}).where(Status.id == status.id)

        # Create a redis notification
        like_status(status, self.user)
        
        return True

    def dislike(self, status):

        # Check if the like exists
        like = Like.get_or_none(user=self.user,status=status)
        if not like:
            return False 
        like.delete().execute()
        Status.update({Status.favourites_count: Status.favourites_count - 1}).where(Status.id == status.id)

    
    def is_following(self, target: UserProfile):
        """
        Return whether the current user is following the `target` user
        """
        
        # Call the current method in models
        # TODO: store this on redis
        return self.user.is_following(target)

    async def is_following_async(self, app, target):
        from models.followers import FollowerRelation

        count = await app.count(FollowerRelation
                .select()
                .where(
                    (FollowerRelation.user == self.user) &
                    (FollowerRelation.follows == target))
                )

        return count > 0

def valid_username(username):
    regex = r'[\w\d_.]+$'
    return re.match(regex, username) != None

def new_user(username, password, email,
             is_remote = False, confirmed=False, is_private = False, 
             is_admin=False, public_key=None, name=None, description = "", ap_id = None, public_inbox=None):

    """
        Returns False or UserProfile
    """
    
    # Verify username

    logging.debug(f"Starting to create user {username}")

    if not valid_username(username):
        logger.error(f"@{username} is a not valid username")
        return False

    # Hash the password
    passw = bcrypt.hashpw(password, salt_code)

    # First we create the actual user

    user = User.create(
        username = username,
        password = passw,
        email = email, 
        confirmed = confirmed,
        is_admin = is_admin,
        is_private = is_private,
    )

    logging.debug(f"Created user {user.username}")

    if name == None:
        name = username

    # Now we create the profile
    try:
        profile = UserProfile.create(
            id = user.id,
            disabled = True,
            is_remote = is_remote,
            user = user,
            name = name,
            public_key = public_key,
            ap_id = ap_id,
            description = description,
            public_inbox = public_inbox

        )

        # Send the confirmation email

        if not user.confirmed:
            send_activation_email(profile)
        
        logging.info(f"New Profile created: {profile}")
        return profile
    except Exception as e:
        logging.error(e)
        user.delete_instance()
        return False

async def new_user_async(username : str, 
                    password : str, 
                    email : str,
                    is_remote : bool = False, 
                    confirmed : bool = False, 
                    is_private : bool  = False, 
                    is_admin : bool = False, 
                    public_key : str = None, 
                    name : str = None, 
                    description : str = "", 
                    ap_id : str = None,
                    send_confirmation: bool = True,
                    public_inbox: Union[str, None] = None) -> Union[bool,UserProfile]:

    """
        Returns False or UserProfile
    """

    if not (password and username and email):
        return False

    objects = Manager(db)
    
    # Verify username

    logging.debug(f"Starting to create user {username}")
    
    username_count = await objects.count(User.select().where(User.username==username))
    
    if not valid_username(username) or (username_count != 0):
        logger.error(f"@{username} is a not valid username")
        return False

    # Hash the password
    passw = bcrypt.hashpw(password, salt_code)

    # First we create the actual user
    try:
        user = await objects.create(User,
            username = username.lower(),
            password = passw,
            email = email, 
            confirmed = confirmed,
            is_admin = is_admin,
            is_private = is_private,
        )
    except Exception as e:
        logging.error(f"User not created: {e}")
        return False

    logging.debug(f"Created user {user.username}")

    if name == None:
        name = username

    # Now we create the profile
    try:

        data = {
            "id": user.id,
            "disabled": True,
            "is_remote": is_remote,
            "user":  user,
            "name":  name,
            "public_key":  public_key,
            "description": description,
            'public_inbox': public_inbox

        }

        if is_remote:
            data['ap_id'] = ap_id
        else:
            data['ap_id'] = uri("user", {"username":username})

        profile = await objects.create(UserProfile,**data)

        # Send the confirmation email

        if not user.confirmed and send_confirmation:
            send_activation_email(profile)
        
        logging.info(f"New Profile created: {profile}")
        return profile
    except Exception as e:
        logging.error(e)
        await objects.delete(user)
        return False
