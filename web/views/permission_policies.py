import json

from sqlalchemy import text
from flask import Response, request
from database import db_session
from flask_restx import fields, Resource, Namespace
from webauth import auth
import uuid

api = Namespace('user_policy', "Policy related operations")

permission_policy_model_create = api.model('Permission Policy Creation', {
    'description': fields.String(description='Description of the Policy'),
    'title': fields.String(description='Name of the Policy')
})

permission_policy_model = api.model('Permission Policy', {
    'id': fields.String(description='ID of the Policy'),
    'description': fields.String(description='Description of the Policy'),
    'title': fields.String(description='Name of the Policy')
})


def get_permission_policy(policy_id):
    result = db_session.execute(text(
        "Select * from vault.PermissionPolicies where Id=:id"
    ), {"id": policy_id}).all()
    return result


def parse_to_permission_policy(row):
    return {
        'id': row[0],
        'description': row[1],
        'title': row[2]
    }


@api.route("/")
class GetAllPolicies(Resource):
    @api.doc(
        "Get metadata for all polices in the vault",
    )
    @api.response(200, 'Success', permission_policy_model)
    @api.response(404, 'No Policies Found', permission_policy_model)
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self):
        result = db_session.execute(text(
            "Select * from vault.PermissionPolicies limit 100"
        )).all()
        return Response(response=json.dumps([parse_to_permission_policy(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.response(201, 'Policy Created', permission_policy_model)
    @api.response(400, 'Bad Response')
    @api.expect(permission_policy_model_create)
    @api.doc(security="basicAuth")
    @auth.login_required
    def post(self):
        try:
            json_data = request.get_json(force=True)
            description = json_data['description']
            title = json_data['title']
            policy_uuid = uuid.uuid4()
            db_session.execute(text(
                "Insert into vault.PermissionPolicies values (:uuid, :title, :description);"), {
                "uuid": policy_uuid,
                "title": title,
                "description": description
            })
            db_session.commit()
            return Response(response=json.dumps(parse_to_permission_policy(get_permission_policy(policy_uuid)[0])),
                            status=201,
                            mimetype='application/json')
        except KeyError as e:
            return Response(response=json.dumps({"error": "A value for {0} in the body was not included. "
                                                          "Please resubmit your request".format(e)}),
                            status=400,
                            mimetype='application/json')
        except Exception:
            return Response(response=json.dumps({"error": "An error occurred while creating the secret. Please check "
                                                          "the logs."}),
                            status=500,
                            mimetype='application/json')


@api.route("/<string:policy_id>")
class GetSecret(Resource):
    @api.doc(
        "Get metadata for a policy in the vault",
    )
    @api.response(200, 'Success', permission_policy_model)
    @api.response(404, 'No Secret Found')
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self, policy_id):
        result = get_permission_policy(policy_id)
        return Response(response=json.dumps([parse_to_permission_policy(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.doc(
        "Delete a policy from the vault",
    )
    @api.response(204, 'Policy Deleted')
    @api.response(404, 'No Policy Found')
    @api.doc(security="basicAuth")
    @auth.login_required
    def delete(self, policy_id):
        old_secret = get_permission_policy(policy_id)
        if len(old_secret) == 0:
            return Response(status=404,
                            mimetype='application/json')

        db_session.execute(text(
            "Delete from vault.PermissionPolicies where Id = :uuid;"),
            {"uuid": policy_id}
        )
        db_session.commit()

        return Response(status=204,
                        mimetype='application/json')
