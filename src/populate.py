import datetime

import argon2

from auth import Argon2
from storage import *

connect()
create_tables()

passw = Argon2().generate_password_hash("yabirIn")

#yab = User.create(username="yab")
yab, created = User.get_or_create(username="yab", password=passw, admin=True)
#me = Photo.create(title=datetime.datetime.now(), user=yab)

photos = (Photo.select().where(Photo.upload_date >= datetime.date.today()))

for photo in photos:
    print(photo)
    print(photo.json())
