import tornado
import json
from settings import DEBUG


class CustomError(tornado.web.HTTPError):
    pass

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE, PATCH')
        self.set_header('Content-Type', 'application/json')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def write_error(self, status_code, **kwargs):

        self.set_header('Content-Type', 'application/json')
        if DEBUG:
            # in debug mode, try to send a traceback
            if self.settings.get("serve_traceback") and "exc_info" in kwargs:
                lines = []
                self.finish(json.dumps({
                    'error': {
                        'code': status_code,
                        'message': self._reason,
                        'traceback': lines,
                    }
                }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))