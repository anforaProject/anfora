from models.photo import Photo
from models.user import User
from activityPub import activities

from tasks.config import huey # import the huey we instantiated in config.py

@huey.task()
def handle_follow(activity):
    followed = User.get_or_none(ap_id=activity.object)
    print("=> Handling follow")
    if followed:
        if isinstance(activity.actor, activities.Actor):
            ap_id = activity.actor.id
        elif isinstance(activity.actor, str):
            ap_id = activity.actor

        follower = get_or_create_remote_user(ap_id)
        FollowerRelation.create(
            user = follower,
            follows = followed
        )

        response = {"Type": "Accept", "Object":activity}


    else:
        print("error handling follow")

@huey.task()
def send_activity(activity, actor):
    # Expects activity to be an already signed activity 
    # as a python dict

    date = f"{datetime.utcnow():%a, %d %b %Y %H:%M:%S} GMT"

    signed_string = f'(request-target): post /inbox\nhost: mastodon.social\ndate: {date}'
    