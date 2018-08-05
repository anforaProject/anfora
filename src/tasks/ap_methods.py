import requests
import logging 

from settings import DOMAIN

from models.status import Status
from models.user import UserProfile


from activityPub import activities
from activityPub.data_signature import *

from api.v1.helpers import sign_data

from tasks.config import huey # import the huey we instantiated in config.py


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@huey.task()
def handle_follow(activity):
    followed = UserProfile.get_or_none(ap_id=activity.object)
    print("=> Handling follow")
    if followed:
        if isinstance(activity.actor, activities.Actor):
            ap_id = activity.actor.id
        elif isinstance(activity.actor, str):
            ap_id = activity.actor

        follower = ActivityPubId(ap_id).get_or_create_remote_user()
        FollowerRelation.create(
            user = follower,
            follows = followed
        )

        response = {"Type": "Accept", "Object":activity}


    else:
        print("error handling follow")

#@huey.task(retries=5, retry_delay=60)
def send_activity(activity, actor, target):
    """
    activity: A object ready to make json dumps and be sent.
    actor   : An instance of User
    target  : A string representing the url objetive of the request
    """

    target = f'{target}/inbox'

    headers = {
        'date': f'{datetime.datetime.utcnow():%d-%b-%YT%H:%M:%SZ}',
        "(request-target)": target,
        "content-type": "application/activity+json",
        "host": DOMAIN,                
    }

    signature = SignatureVerification(headers, 'post', target).sign(actor)
    headers.update({'signature': signature})
    
    print("=======================")
    print(headers)
    print(activity)
    print(target)
    print("=======================")
    r = requests.post(target, data=json.dumps(activity), headers=headers)
    print(r.text)
    print(r.status_code)

    
    