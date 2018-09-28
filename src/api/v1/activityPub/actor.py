class getActor():
    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, username):
        person = User.get_or_none(username=username)
        if person:
            person = person.profile.get()
            resp.body = json.dumps(person.to_json(), default=json_serial)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404
