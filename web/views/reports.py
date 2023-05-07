import json

from webauth import auth
from sqlalchemy import text, select
from flask import Blueprint, jsonify, Response
from database import db_session
from flask_restx import fields, Resource, Namespace

api = Namespace('reports', "Reporting related operations")

secret_report_model = api.model('SecretReport', {
    'id': fields.String(description='ID of the Secret'),
    'value': fields.String(description='Number of Events for the secret'),
})

policy_report_model = api.model('PolicyReport', {
    'id': fields.String(description='ID of the Policy'),
    'value': fields.String(description='Number of Users assigned the policy'),
})


@api.route("/secret-events")
class GetAllEvents(Resource):
    @api.doc(
        "Get number of events per secret",
        responses={
            200: "Event Data Found",
            404: "No Events Found",
        },
    )
    @api.response(200, "Event Data Found", secret_report_model)
    @api.response(400, "No Events Found")
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self):
        from views.secrets import get_secrets_for_user
        result = db_session.execute(text("Select v.SecretId, count(*) "
                                         "from vault.v_SecretEvents v group by v.SecretId;")).all()
        secrets = list(i[0] for i in get_secrets_for_user(auth.current_user()))
        filtered_events = [{"id": i[0], "value": i[1]} for i in result if i[0] in secrets]
        return Response(response=json.dumps(filtered_events),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')


@api.route("/user-policies")
class GetAllEvents(Resource):
    @api.doc(
        "Get number of users per policy",
        responses={
            200: "Event Data Found",
            404: "No Events Found",
        },
    )
    @api.response(200, "Policy Data Found", secret_report_model)
    @api.response(400, "No Events Found")
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self):
        result = db_session.execute(text("select pp.Id, count(distinct(UP.UserId)) as NumUsers from "
                                         "PermissionPolicies as pp join UserPermissions UP on pp.Id = "
                                         "UP.PermissionPolicyId group by pp.Id")).all()
        policy_counts = [{"id": i[0], "value": i[1]} for i in result]
        return Response(response=json.dumps(policy_counts),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')
