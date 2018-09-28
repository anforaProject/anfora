import falcon
import os

from settings import ROOT_PATH
class VueClient:
    auth = {
        'exempt_methods': ['GET']
    }

    def _load_template(self, name):
        path = os.path.join(ROOT_PATH, 'src/client/dist', name)
        with open(os.path.abspath(path), 'r') as fp:
            return fp.read()


    def on_get(self, req, resp):
        html = self._load_template('index.html')
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        resp.body = html