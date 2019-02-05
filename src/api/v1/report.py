import json
import os
import logging
import uuid
import io
import sys

from api.v1.base_handler import BaseHandler, CustomError

logger = logging.getLogger(__name__)

from models.report import Report, topics
from auth.token_auth import (bearerAuth, is_authenticated)

class Report(BaseHandler):

    async def get(self, id):

        report = Report.get_or_none(Report.id == id)
        if report and req.context['user'].is_admin:
            resp.body = json.dumps(report.json())
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'Error': 'Report not found'})

    @bearerAuth
    async def post(self, user):

        # Id of the user being reported
        try:
            target = int(self.get_argument('target', False))
        except: 
            raise CustomError(reason="Target user not provided", status_code=404)
            logger.error("Id of target couldn't be converted to int or is not present")

        
        user_target = await self.application.objects.get(UserProfile, id=target)

        if not user_target:
            raise CustomError(reason="Target provided is not valid", status_code=404)

        # Id of the user reporting 
        reporter = user.id

        # Message of the report
        message = self.get_param('message', default="")

        # Reason of the report
        reason = self.get_param('reason', default="Not expecified")

        

        report = Report.create(
            target = user_target,
            reporter = reporter,
            message = message,
            reason = reason
        )

        resp.body = json.dumps(report.json())
        resp.status = falcon.HTTP_200            