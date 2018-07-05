import falcon

from api.v1.helpers import load_template

class VueClient:
    auth = {
        'exempt_methods': ['GET']
    }
    def on_get(self, req, resp, path):
        html = load_template('index.html')

        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        resp.body = html