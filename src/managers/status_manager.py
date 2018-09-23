from models.status import Status 
from models.user import UserProfile
from models.like import Like
from models.media import Media

from tasks.redis.spreadStatus import like_status
from tasks.redis.remove_status import remove_status
from tasks.redis.spreadStatus import spread_status


class StatusManager:

    def __init__(self, id):
        
        """
            id: int - Id of the status representing
        """

        self.status = Status.get_or_none(Status.id == id)
        self.LIVE_UPDATES = 'timeline:{}'

        if not self.status:
            raise ValueError(f'Could not find status with id {id}')


        self.id = id

    def create(self, user, caption, sensitive, public, spoiler = None, 
                    remote=False, story=False, media_ids):
        """
            user: UserProfile - User creating the status
            caption: str - Image caption
            sensitive: bool - Content has something sensitive.
            spoiler: str - Content spoiler text
            public: bool - True if yes
            media_ids: list - A list with the media related to the status

            Returns the created status

        """

        status = Status.create (
                    caption = caption,
                    is_public = public,
                    user = user,
                    sensitive = sensitive,
                    spoiler_text = spoiler,
                    remote = remote,
                    is_story = story
                )

        for image in req.get_param('media_ids').split(','):
            m = Media.get_or_none(media_name=image)
            m.status = status
            m.save()

        UserProfile.update({UserProfile.statuses_count: UserProfile.statuses_count + 1}).where(UserProfile.id == status.user.id).execute()
        spread_status(status)

    def notify_creation(follower_id, json_data):
        r.publish(self.LIVE_UPDATES.format(follower_id), f'update {json_file}')

    def delete(self):
        # Deleting the status should delete likes and all the things depending on it
        remove_status(status)

