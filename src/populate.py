import datetime
import random 
import json
import string
import io
import os
from base64 import b64encode

from falcon import testing

from models.user import UserProfile, User
from models.status import Status
from models.followers import FollowerRelation
from manage_db import (connect, create_tables)

from managers.user_manager import new_user


from main import app

PHOTOS = 20

def random_string(n):
    return ''.join(random.sample((string.ascii_uppercase+string.digits),n))

def create_multipart(data, fieldname, filename, content_type):
    """
    Basic emulation of a browser's multipart file upload
    """
    boundry = '----WebKitFormBoundary' + random_string(16)
    buff = io.BytesIO()
    buff.write(b'--')
    buff.write(boundry.encode())
    buff.write(b'\r\n')
    buff.write(('Content-Disposition: form-data; name="%s"; filename="%s"' % \
               (fieldname, filename)).encode())
    buff.write(b'\r\n')
    buff.write(('Content-Type: %s' % content_type).encode())
    buff.write(b'\r\n')
    buff.write(b'\r\n')
    buff.write(data)
    buff.write(b'\r\n')
    buff.write(boundry.encode())
    buff.write(b'--\r\n')
    headers = {'Content-Type': 'multipart/form-data; boundary=%s' %boundry}
    headers['Content-Length'] = str(buff.tell())
    return buff.getvalue(), headers

connect()
create_tables()

passw = Argon2().generate_password_hash("test")

#yab = UserProfile.create(username="yab")
yab = new_user(
        username = "test", 
        password = 'test', 
        email = "yab2@gmail.com",
        description="A test user",
        confirmed=True,
        is_admin = True,
        is_remote=False,
        is_private=False
    )
    
def populate_db():
    for i in range(15):
        target = UserProfile.create(
            username=f'test{i}',
            password=passw,
            name=f'test#{i}',
            email=f'fort{i}@gma.com',
            confirmation_sent_at=datetime.datetime.now(),
            last_sign_in_at=1
        )

        print(f"Created user {target.username}")

        target.follow(yab)

        print("Following user")
        #crate some followers
        for j in range(i):
            if j != i:
                user = UserProfile.get(username=f'test{j}')
                print(f'{user.username} -> {target.username}')
                user.follow(target, True)

        #craete some images via API
        print("Uploading some pics")
        for j in range(PHOTOS):
            print(f'Image {j} of {PHOTOS}')
            client = testing.TestClient(app)

            data = {
                'username': target.username,
                'password': 'test'
            }

            header = {
                'Authorization':"Basic " + b64encode(f"{data['username']}:{data['password']}".encode()).decode('utf-8')
            }

            token = client.simulate_get("/api/v1/auth", json=data, headers=header)
            token = token.json['token']

            auth = {
                'Authorization': token
            }
            
            images = ['fine.jpg', 'wildunix.jpeg', 'gatos.jpeg']
            image = random.choice(images)

            ids = []

            data, headers = create_multipart( open(f'tests/assets/{image}', 'rb').read(), fieldname="file",
                                    filename='image',
                                    content_type=f'image/{image.split(".")[1]}')


            auth.update(headers)
            response = client.simulate_post("/api/v1/media", body=data, headers=auth)
            ids.append(response.json['id'])

            status = {
                'visibility': True,
                'status': f'My photo #{j} by @{target.username}',
                'sensitive': random.choice([True, False]),
                'media_ids': ','.join(ids)
            }

            response = client.simulate_post("/api/v1/statuses", params=status, headers=auth)

def populate_for_travis():
    for i in range(15):
        target = new_user(
            username=f'test{i}', 
            password = passw, 
            email=f'fort{i}@gma.com',
            confirmed=True,
            is_admin = True,
            is_remote=False,
            is_private=False
        )
        target.follow(yab)

        #crate some followers
        for j in range(i):
            if j != i:
                user = User.get(username=f'test{j}').profile.get()
                user.follow(target, True)

if os.environ.get('POPULATE', 'local') == 'travis':
    populate_for_travis()
else:
    populate_db()