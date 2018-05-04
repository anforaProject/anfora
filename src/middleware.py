# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import falcon
import peewee

from models.base import db as database

class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        database.connect()

    def process_response(self, req, resp, resource):
        if not database.is_closed():
            database.close()
