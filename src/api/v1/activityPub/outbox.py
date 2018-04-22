import json
import falcon

from models.user import User
from models.photo import Photo
from models.followers import FollowerRelation

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import deliver, store

from api.v1.activityPub.methods import get_or_create_remote_user

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
                user = req.context['user']
                filename = image.filename
                photo = Photo.create(title=filename,
                                     public=public,
                                     user=user,
                                     media_type=1)
                print(photo, self.uploads)

                try:
                    file_path = os.path.join(self.uploads, photo.media_name)
                    temp_file = file_path + '~'
                    open(temp_file, 'wb').write(image.file.read())
                    os.rename(temp_file, file_path)


                except Exception as e:
                    print(e)
                    photo.delete_instance()
                    resp.status = falcon.HTTP_500
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
            print(followed.ap_id, user.username, followed.username)
            #FollowerRelation.create(user = user, follows=followed)

            activity.actor = user.uris.id
            activity.to = followed.uris.id
            activity.id = store(activity, user)
            resp.body = json.dumps({"Success": "Delivered successfully"})
            resp.status = falcon.HTTP_200
