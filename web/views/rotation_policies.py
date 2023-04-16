import json

from sqlalchemy import text
from flask import Response, request
from database import db_session
from flask_restx import fields, Resource, Namespace
import uuid

api = Namespace('rotation_policy', "Rotation Policy related operations")


rotation_policy_model_create = api.model('Rotation Policy Creation', {
    'description': fields.String(description='Description of the Policy'),
    'title': fields.String(description='Name of the Policy'),
    'hours': fields.Integer(description='Hours after which to rotate the secret')
})

rotation_policy_model = api.model('Rotation Policy', {
    'id': fields.String(description='ID of the Policy'),
    'description': fields.String(description='Description of the Policy'),
    'title': fields.String(description='Name of the Policy'),
    'hours': fields.Integer(description='Hours after which to rotate the secret')
})


def get_permission_policy(policy_id):
    result = db_session.execute(text(
        "Select * from vault.RotationPolicies where Id=:id"
    ), {"id": policy_id}).all()
    return result


def parse_to_permission_policy(row):
    return {
        'id': row[0],
        'description': row[1],
        'title': row[2],
        'hours': row[3]
    }


@api.route("/")
class GetAllPolicies(Resource):
    @api.doc(
        "Get metadata for all polices in the vault",
    )
    @api.response(200, 'Success', rotation_policy_model)
    @api.response(404, 'No Policies Found')
    def get(self):
        result = db_session.execute(text(
            "Select * from vault.RotationPolicies"
        )).all()
        return Response(response=json.dumps([parse_to_permission_policy(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.response(201, 'Policy Created', rotation_policy_model)
    @api.response(400, 'Bad Response')
    @api.expect(rotation_policy_model_create)
    def post(self):
        try:
            json_data = request.get_json(force=True)
            description = json_data['description']
            title = json_data['title']
            hours = json_data['hours']
            policy_uuid = uuid.uuid4()
            db_session.execute(text(
                "Insert into vault.RotationPolicies values (:uuid, :title, :description, :hours);"), {
                "uuid": policy_uuid,
                "title": title,
                "description": description,
                "hours": int(hours)
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
    @api.response(200, 'Success', rotation_policy_model)
    @api.response(404, 'No Secret Found')
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
    def delete(self, policy_id):
        old_secret = get_permission_policy(policy_id)
        if len(old_secret) == 0:
            return Response(status=404,
                            mimetype='application/json')

        db_session.execute(text(
            "Delete from vault.RotationPolicies where Id = :uuid;"),
            {"uuid": policy_id}
        )
        db_session.commit()

        return Response(status=204,
                        mimetype='application/json')
