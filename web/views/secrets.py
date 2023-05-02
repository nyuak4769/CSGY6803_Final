import datetime
import json
import logging

from sqlalchemy import text
from flask import Response, request
from database import db_session
from flask_restx import fields, Resource, Namespace
from webauth import auth
import uuid

api = Namespace('secret', "Secret related operations")


def parse_to_secret(row):
    return {
        'id': row[0],
        'description': row[1],
        'rotationpolicy': row[3],
        'nextrotationtime': row[2].isoformat(),
        'permissionPolicies': list(str(row[4]).split(","))
    }


def get_secret_info(secret_id):
    result = db_session.execute(text(
        "Select * from v_SecretDetails where Id = :id"
    ), {"id": secret_id}).all()
    return result


def get_user_policies():
    result = db_session.execute(text(
        "Select Id from vault.PermissionPolicies"
    )).all()
    return result


def get_rotation_policies():
    result = db_session.execute(text(
        "Select Id from vault.RotationPolicies"
    )).all()
    return result


def get_user_policies_for_secret(secret_id):
    result = db_session.execute(text(
        "Select PermissionPolicyId from vault.SecretPermissions where SecretId = :secretId"
    ), {
        "secretId": secret_id
    }).all()
    return result


secret_model = api.model('Secrets', {
    'id': fields.String(description='ID of the Secret'),
    'description': fields.String(description='Description of the Secret'),
    'rotationpolicy': fields.String(description='Name of the Rotation Policy for the Secret'),
    'nextrotationtime': fields.String(description='UTC Timestamp of the next rotation in ISO8601 Format'),
    'userpolicies': fields.List(fields.String, description='List of Permission Policies which can access the Secret')
})

secret_model_create = api.model('Secret Creation', {
    'description': fields.String(description='Description of the Secret'),
    'policyname': fields.String(description='Name of the Rotation Policy for the Secret'),
    'value': fields.String(description='Value of the secret to store'),
})

secret_model_patch = api.model('Secret Policy', {
    'rotationpolicy': fields.String(description='Rotation Policy ID'),
    'userpolicies': fields.String(description='Comma Separated list of Policy ID for users')
})

@api.route("/")
class GetAllSecrets(Resource):
    @api.doc(
        "Get metadata for all secrets in the vault",
    )
    @api.response(200, 'Success', secret_model)
    @api.response(404, 'No Secrets Found', secret_model)
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self):
        result = db_session.execute(text(
            "Select * from v_SecretDetails"
        )).all()
        return Response(response=json.dumps([parse_to_secret(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.response(201, 'Secret Created', secret_model)
    @api.response(400, 'Bad Response')
    @api.expect(secret_model_create)
    @api.doc(security="basicAuth")
    @auth.login_required
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
class GetSecretMetadata(Resource):
    @api.doc(
        "Get metadata for a secret in the vault",
    )
    @api.response(200, 'Success', secret_model)
    @api.response(404, 'No Secret Found', secret_model)
    @api.doc(security="basicAuth")
    @auth.login_required
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
    @api.doc(security="basicAuth")
    @auth.login_required
    def delete(self, secret_id):
        old_secret = get_secret_info(secret_id)
        if len(old_secret) == 0:
            return Response(status=404,
                            mimetype='application/json')

        db_session.execute(text(
            "CALL usp_DeleteSecretById(:uuid);"),
            {"uuid": secret_id}
        )
        db_session.commit()

        return Response(status=204,
                        mimetype='application/json')

    @api.doc(
        "Update policies for a secret in the vault",
    )
    @api.response(204, 'Secret Updated')
    @api.response(404, 'No Secret Found')
    @api.doc(security="basicAuth")
    @api.expect(secret_model_patch)
    @auth.login_required
    def patch(self, secret_id):
        json_data = request.get_json(force=True)

        if "rotationpolicy" in json_data:
            if json_data['rotationpolicy'] not in list(i[0] for i in get_rotation_policies()):
                return Response(status=400,
                                response=json.dumps({"error": "Rotation Policy is not valid"}),
                                mimetype='application/json')
            else:
                db_session.execute(text("UPDATE vault.Secrets SET RotationPolicyID = :policyId where Id = :secretId"),
                                   {
                                       "secretId": secret_id,
                                       "policyId": json_data['rotationpolicy']
                                   })

        if "userpolicies" in json_data:
            user_policies = list(i[0] for i in get_user_policies())
            db_session.execute(text("Delete from vault.SecretPermissions where SecretId = :secretId"),
                               {
                                   "secretId": secret_id,
                               })
            for p in json_data['userpolicies'].split(","):
                if p not in user_policies:
                    return Response(status=400,
                                    response=json.dumps({"error": "User Policy is not valid"}),
                                    mimetype='application/json')
                else:
                    db_session.execute(text("Insert into vault.SecretPermissions (SecretId, PermissionPolicyId) "
                                            "VALUES (:secretId, :permissionId)"),
                                       {
                                           "secretId": secret_id,
                                           "permissionId": p
                                       })
        db_session.commit()

        return Response(status=204,
                        mimetype='application/json')

@api.route("/<string:secret_id>/retrieve")
class GetSecretValue(Resource):
    @api.doc(
        "Get value for a secret in the vault",
    )
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self, secret_id):
        old_secret = get_secret_info(secret_id)
        if len(old_secret) == 0:
            return Response(status=404,
                            mimetype='application/json')

        result = db_session.execute(text(
            "CALL usp_RetrieveSecretById(:uuid);"),
            {"uuid": secret_id}
        ).all()

        db_session.commit()

        return Response(status=200,
                        response=json.dumps({"password": result[0][1]}),
                        mimetype='application/json')