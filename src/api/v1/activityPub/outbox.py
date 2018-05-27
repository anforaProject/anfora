import json
import os, sys, io
import uuid

from PIL import Image
import falcon

from models.user import User
from models.photo import Photo
from models.followers import FollowerRelation
from models.activity import Activity

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import  store
from tasks.tasks import deliver
from tasks.tasks import create_image

from api.v1.activityPub.methods import get_or_create_remote_user


class Outbox():

    def __init__(self):
        self.uploads = os.getenv('UPLOADS', '/home/yabir/killMe/uploads')

    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, username):
        user = User.get_or_none(username==username)
        objects = user.photos.select().order_by(Photo.created_at.desc())

        collection = activities.OrderedCollection(map(activities.Note, objects))
        resp.body = json.dumps(collection.to_json(context=True))
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, username):
        user = User.get_or_none(username==username)

        if req.context['user'].username != username:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Access denied"})

        payload = req.get_param('data')
        activity = json.loads(payload, object_hook=as_activitystream)

        if activity.object.type == "Note":
            obj = activity.object
            activity = activities.Create(
                to=user.uris.followers,
                actor=user.uris.id,
                object=obj
            )

        activity.validate()

        if activity.type == "Create":
            if activity.object.type != "Note":
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "You only can create notes"})

            image = req.get_param('image')
            if image != None and image.filename:
                try:

                    #Search a valid name

                    valid = False
                    ident = ""
                    while not valid:
                        ident = str(uuid.uuid4())
                        valid = not Photo.select().where(Photo.media_name == ident).exists()

                    #Pick the images paths
                    file_path = os.path.join(self.uploads, ident)

                    #temp_file = file_path + '~'
                    #open(temp_file, 'wb').write(image.file.read())

                    #Create the image and the thumbnail
                    create_image(io.BytesIO(image.file.read()), file_path)

                    user = req.context['user']
                    filename = image.filename
                    width, height = (1080,1080)

                    photo = Photo.create(title=filename,
                                         user=user,
                                         message = activity.object.message or '',
                                         description = activity.object.description or '',
                                         sensitive = activity.object.sensitive or '',
                                         media_type="Image",
                                         width = width,
                                         height=height,
                                         media_name=ident,
                                         )

                except IOError:
                    print(e)
                    photo.delete_instance()
                    resp.body = json.dumps({"Error": "Couldn't store file"})
                    resp.status = falcon.HTTP_500

                activity.object.id = photo.uris.id
                activity.id = store(activity, user)
                #deliver(activity)
                resp.body = json.dumps({"Success": "Delivered successfully"})
                resp.status = falcon.HTTP_200

                #Convert to jpeg

            else:
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "No photo attached"})




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
