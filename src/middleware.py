# -*- coding: utf-8 -*-

import falcon
import peewee

from models.base import db as database

class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        database.connect()

    def process_response(self, req, resp, resource):
        if not database.is_closed():
            database.close()

class CorsMiddleware(object):

    def process(self, req, resp):
         resp.set_header('access-control-allow-credentials', 'true')
         resp.set_header('access-control-allow-methods', '*')
         resp.set_header('access-control-allow-headers', '*')
         resp.set_header('access-control-allow-origin', '*')
         resp.status = falcon.HTTP_200


    def process_response(self, req, resp, resource):
         resp.set_header('access-control-allow-credentials', 'true')
         resp.set_header('access-control-allow-methods', '*')
         resp.set_header('access-control-allow-headers', 'authorization,content-type')
         resp.set_header('access-control-allow-origin', '*')
         resp.status = falcon.HTTP_200
