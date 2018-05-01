import json
import (os, sys, io)

from PIL import Image
import falcon

from models.user import User
from models.photo import Photo
from models.followers import FollowerRelation

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import deliver, store

from api.v1.activityPub.methods import get_or_create_remote_user

THUMBNAIL_SIZE = (320, 320)
DEFAULT_BOX = (0,0,1080, 1080)
class Outbox():

    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, username):
        user = User.get_or_none(username==username)
        objects = user.activities.select().where(remote==False).order_by(created_at.desc())

        collection = activities.OrderedCollection(objects)
        resp.body = collection.to_json(context=True)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, username):
        user = User.get_or_none(username==username)

        if req.context['user'].username != username:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Access denied"})

        payload = req.stream.read().decode("utf-8")
        activity = json.loads(payload, object_hook=as_activitystream)

        if activity.type == "Note":
            obj = activity
            activity = activities.Create(
                to=person.uris.followers,
                actor=person.uris.id,
                object=obj
            )

        activity.validate()

        if activity.type == "Create":
            if activity.object.type != "Note":
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "You only can create notes"})

            content = activity.object.content
            image = req.get_param('image')
            if image.filename:
                try:
                    file_path = os.path.join(self.uploads, photo.media_name)
                    thumb, file_path = os.path.splitext(file_path)[0]+'.thumbnail', os.path.splitext(file_path)[0]+'.jpg'
                    #temp_file = file_path + '~'
                    #open(temp_file, 'wb').write(image.file.read())
                    im = Image.open(io.BytesIO(image.file.read()))
                    im.crop(DEFAULT_BOX)
                    im.resize((1080, 1080))
                    im.save(file_path)
                    im.thumbnail(THUMBNAIL_SIZE).save(thumb, "JPG")

                    user = req.context['user']
                    filename = image.filename
                    width, height = im.size()
                    photo = Photo.create(title=filename,
                                         user=user,
                                         public = activity.public or True,
                                         message = activity.message or '',
                                         description = activity.description or '',
                                         sensitive = activity.sensitive or '',
                                         media_type="Image",
                                         width = width,
                                         height=height,
                                         )

                except IOError:
                    print(e)
                    photo.delete_instance()
                    resp.body = json.dumps({"Error": "Couldn't store file"})
                    resp.status = falcon.HTTP_500

                #Convert to jpeg

            else:
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "No photo attached"})

            activity.object.id = photo.uris.id
            activity.id = store(activity, user)
            deliver(activity)
            resp.body = json.dumps({"Success": "Delivered successfully"})
            resp.status = falcon.HTTP_200


        if activity.type == "Follow":
            # if activity.object.type != "Person":
            #     raise Exception("Sorry, you can only follow Persons objects")

            followed = get_or_create_remote_user(activity.object)
            user = req.context["user"]
            #print(followed.ap_id, user.username, followed.username)
            f = FollowerRelation.create(user = user, follows=followed)
            print("=> {} starts process to follow {}".format(user.username, followed.username))
            activity.actor = user.uris.id
            activity.to = followed.uris.id
            #activity.id = store(activity, user)
            deliver(activity)

            resp.body = json.dumps({"Success": "Delivered successfully"})
            resp.status = falcon.HTTP_200
