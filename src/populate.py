import datetime

import argon2

from auth import Argon2
from models.user import User
from models.photo import Photo

from manage_db import (connect, create_tables)

connect()
create_tables()

passw = Argon2().generate_password_hash("yabirIn")

#yab = User.create(username="yab")
yab, created = User.get_or_create(username="yab",
                                  defaults={
                                      'password':passw,
                                      'admin':True,
                                      'email':"test@gt.com",
                                      'confirmation_sent_at':datetime.datetime.now(),
                                      'last_sign_in_at':1
                                  })
"""
photos = (Photo.select().where(Photo.upload_date >= datetime.date.today()))

for photo in photos:
    print(photo)
    print(photo.json())

"""
