import json

import falcon

from models.report import Report, topics

class Report:

    def on_get(self, req, resp, id):

        report = Report.get_or_none(Report.id == id)
        if report and req.context['user'].is_admin:
            resp.body = json.dumps(report.json())
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'Error': 'Report not found'})

    def on_post(self, req, resp):
        target = req.get_param_as_int('target', required=True, min=0)
        reporter = req.context['user']
        message = req.get_param('message', default="")
        reason = req.get_param('reason', required=True)
        
        user_target = UserProfile.get_or_none(id=target)
        
        if user_target and reason in topics:
            report = Report.create(
                target = user_target,
                reporter = reporter,
                message = message,
                reason = reason
            )

            resp.body = json.dumps(report.json())
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({"Error": "Bad topic or no target"})