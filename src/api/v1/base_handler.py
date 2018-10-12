import tornado

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE')
        self.set_header('Content-Type', 'application/json')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()