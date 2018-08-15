# -*- coding: utf-8 -*-

import falcon
import peewee

from models.base import db as database

class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        if database.is_closed():
            database.connect()

    def process_response(self, req, resp, resource):
        if not database.is_closed():
            database.close()

class CorsMiddleware(object):

    def process(self, req, resp):
         resp.set_header('Access-Control-Allow-Credentials', 'true')
         resp.set_header('Access-Control-Allow-Methods', '*')
         resp.set_header('Access-Control-Allow-Headers', '*')
         resp.set_header('Access-Control-Allow-Origin', '*')

    def process_response(self, req, resp, resource):
         resp.set_header('Access-Control-Allow-Credentials', 'true')
         resp.set_header('Access-Control-Allow-Methods', '*')
         resp.set_header('Access-Control-Allow-Headers', '*')
         resp.set_header('Access-Control-Allow-Origin', '*')
