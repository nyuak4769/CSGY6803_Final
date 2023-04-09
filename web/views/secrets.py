import datetime
import json

from sqlalchemy import text
from flask import Response, request
from database import db_session
from flask_restx import fields, Resource, Namespace
import uuid

api = Namespace('secret', "Secret related operations")


def parse_to_secret(row):
    return {
        'id': row[0],
        'description': row[1],
        'rotationpolicy': row[3],
        'nextrotationtime': row[2].isoformat()
    }


def get_secret_info(secret_id):
    result = db_session.execute(text(
        "Select Secrets.Id, Secrets.Description, nsr.nextRotation, rp.Title from vault.Secrets "
        "join (select SecretId, nextRotation from vault.v_NextSecretRotationTime) as nsr on "
        "Secrets.Id=nsr.SecretId join vault.RotationPolicies as rp on rp.Id=Secrets.RotationPolicyID "
        "where Secrets.Id = :id"
    ), {"id": secret_id}).all()
    return result


secret_model = api.model('Secrets', {
    'id': fields.String(description='ID of the Secret'),
    'description': fields.String(description='Description of the Secret'),
    'rotationpolicy': fields.String(description='Name of the Rotation Policy for the Secret'),
    'nextrotationtime': fields.String(description='UTC Timestamp of the next rotation in ISO8601 Format'),
})

secret_model_create = api.model('Secret Creation', {
    'description': fields.String(description='Description of the Secret'),
    'policyname': fields.String(description='Name of the Rotation Policy for the Secret'),
    'value': fields.String(description='Value of the secret to store'),
})


@api.route("/")
class GetAllSecrets(Resource):
    @api.doc(
        "Get metadata for all secrets in the vault",
    )
    @api.response(200, 'Success', secret_model)
    @api.response(404, 'No Secrets Found', secret_model)
    def get(self):
        result = db_session.execute(text(
            "Select Secrets.Id, Secrets.Description, nsr.nextRotation, rp.Title from vault.Secrets "
            "join (select SecretId, nextRotation from vault.v_NextSecretRotationTime) as nsr on "
            "Secrets.Id=nsr.SecretId join vault.RotationPolicies as rp on rp.Id=Secrets.RotationPolicyID;"
        )).all()
        return Response(response=json.dumps([parse_to_secret(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.response(201, 'Secret Created', secret_model)
    @api.response(400, 'Bad Response')
    @api.expect(secret_model_create)
    def post(self):
        try:
            json_data = request.get_json(force=True)
            description = json_data['description']
            value = json_data['value']
            rotation_policy_name = json_data['policyname']
            secret_uuid = uuid.uuid4()
            db_session.execute(text(
                "Insert into vault.Secrets values (:uuid, :description, :value, "
                "(select Id from vault.RotationPolicies where Title = :policy_name limit 1));"), {
                "uuid": secret_uuid,
                "description": description,
                "value": value,
                "policy_name": rotation_policy_name
            })
            db_session.commit()
            return Response(response=json.dumps(parse_to_secret(get_secret_info(secret_uuid)[0])),
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


@api.route("/<string:secret_id>")
class GetSecret(Resource):
    @api.doc(
        "Get metadata for a secret in the vault",
    )
    @api.response(200, 'Success', secret_model)
    @api.response(404, 'No Secret Found', secret_model)
    def get(self, secret_id):
        result = get_secret_info(secret_id)
        return Response(response=json.dumps([parse_to_secret(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.doc(
        "Delete a secret from the vault",
    )
    @api.response(204, 'Secret Deleted')
    @api.response(404, 'No Secret Found')
    def delete(self, secret_id):
        old_secret = get_secret_info(secret_id)
        if len(old_secret) == 0:
            return Response(status=404,
                            mimetype='application/json')

        db_session.execute(text(
            "Delete from vault.Events where SecretId = :uuid; Delete from vault.Secrets where Id = :uuid;"),
            {"uuid": secret_id}
        )
        db_session.commit()

        return Response(status=204,
                        mimetype='application/json')
