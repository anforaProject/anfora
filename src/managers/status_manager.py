from models.status import Status 
from models.user import UserProfile
from models.like import Like

from tasks.redis.spreadStatus import like_status
from tasks.redis.remove_status import remove_status

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

    def create(self, user, caption, sensitive, spoiler, public, remote=False, story=False):
        """
            user: UserProfile - User creating the status
            caption: str - Image caption
            sensitive: bool - Content has something sensitive.
            spoiler: str - Content spoiler text
            public: bool - True if yes

            Returns the created status

        """

        return Status.create (
                    caption = caption,
                    is_public = public,
                    user = user,
                    sensitive = sensitive,
                    remote = remote,
                    is_story = story
                )

    def notify_creation(follower_id, json_data):
        r.publish(self.LIVE_UPDATES.format(follower_id), f'update {json_file}')

    def delete(self):
        # Deleting the status should delete likes and all the things depending on it
        remove_status(status)

