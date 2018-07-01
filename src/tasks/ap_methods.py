import requests

from settings import DOMAIN

from models.photo import Photo
from models.user import User
from activityPub import activities

from api.helpers import sign_data

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

@huey.task(retries=5, retry_delay=60)
def send_activity(activity, actor, object):
    """
    activity: A object ready to make json dumps and be sent.
    actor   : An instance of User
    object  : A string representing the url objetive of the request
    """

    date = f"{datetime.utcnow():%a, %d %b %Y %H:%M:%S} GMT"


    signed_string = f'(request-target): post /inbox\nhost: {DOMAIN}\ndate: {date}'
    signature = sign_data(signed_string, actor.private_key)
    keyId = actor.uris.id + '#main-key'
    header = f'keyId="{keyId}",headers="(request-target) host date",signature="{signature}"'

    
    headers = {
        'Host': DOMAIN,
        'Date': date,
        'Signature': header
    }

    r = request.post(object, data=json.dumps(activity), headers=headers, timeout=(5, 20))