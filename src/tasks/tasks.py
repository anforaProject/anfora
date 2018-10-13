import os

from PIL import Image

from settings import MEDIA_FOLDER

from models.status import Status
#from api.v1.activityPub.methods import (get_final_audience, deliver_to)

from tasks.config import huey # import the huey we instantiated in config.py

from settings import (thumb_folder, pic_folder)

THUMBNAIL_SIZE = 320, 320
THUMBNAIL_BOX = 0,0, 320, 320
DEFAULT_BOX = 0,0,1080, 1080

sizes = {
    'square': (1080, 1080),
    'landscape': (1920, 1080),
    'portrait': (1080, 1350),
    'thumbnail': (320, 320)
}

@huey.task()
def count_beans(num):
    print('-- counted %s beans --' % num)

@huey.task()
def create_image(bytes, filename):

    thumb = os.path.join(MEDIA_FOLDER, thumb_folder, filename + '.thumbnail')
    file_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + '.jpeg')


    im = Image.open(bytes)
    im.crop(DEFAULT_BOX)
    im.thumbnail((1080, 1080), Image.ANTIALIAS)
    im.save(file_path,'JPEG', quality=80, optimize=True, progressive=True)

    im.crop(THUMBNAIL_BOX)
    im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    im.save(thumb, "jpeg")

@huey.task()
def deliver(activity):
    audience = activity.get_audience()
    activity = activity.strip_audience()
    print("=> audience: {}".format(audience))
    audience = get_final_audience(audience)
    print("delivering", audience)
    for ap_id in audience:
        try:
            deliver_to(ap_id, activity)
        except:
            print("Error delivering")
