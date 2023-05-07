import json
import logging

import sqlalchemy.exc
from sqlalchemy import text
from flask import Response, request
from database import db_session
from flask_restx import fields, Resource, Namespace
from webauth import auth
import bcrypt
import uuid

api = Namespace('users', "User related operations")

user_model_create = api.model('User Creation', {
    'password': fields.String(description='Password of the User'),
    'username': fields.String(description='Username of the User')
})

user_model = api.model('User', {
    'id': fields.String(description='ID of the User'),
    'username': fields.String(description='Username of the User')
})

user_model_update = api.model('User Update', {
    'password': fields.String(description='Password of the User'),
    'policies': fields.String(description='Comma Separated list of Policy Names')
})


def get_user(user_name):
    result = db_session.execute(text(
        "Select Id, UserName from vault.Users where UserName=:id"
    ), {"id": user_name}).all()
    return result


def get_user_hashed_password(user_name):
    result = db_session.execute(text(
        "Select Password from vault.Users where UserName=:id"
    ), {"id": user_name}).all()
    return result


def parse_to_user(row):
    return {
        'id': row[0],
        'username': row[1]
    }


def get_policies():
    result = db_session.execute(text(
        "Select Id, Title from vault.PermissionPolicies"
    )).all()
    return {i[1]: i[0] for i in result}


@api.route("/")
class GetAllUsers(Resource):
    @api.doc(
        "Get metadata for all users in the vault",
    )
    @api.response(200, 'Success', user_model)
    @api.response(404, 'No Users Found', user_model)
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self):
        print(auth.current_user())
        result = db_session.execute(text(
            "Select Id, UserName from vault.Users"
        )).all()
        return Response(response=json.dumps([parse_to_user(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.response(201, 'User Created', user_model)
    @api.response(400, 'Bad Response')
    @api.expect(user_model_create)
    @api.doc(security="basicAuth")
    @auth.login_required
    def post(self):
        try:
            json_data = request.get_json(force=True)
            username = json_data['username']
            password_text = json_data['password']
            password_bytes = password_text.encode('utf-8')
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt)
            user_uuid = uuid.uuid4()
            db_session.execute(text(
                "Insert into vault.Users values (:uuid, :username, :password);"), {
                "uuid": user_uuid,
                "username": username,
                "password": password_hash
            })
            db_session.commit()
            return Response(response=json.dumps(parse_to_user(get_user(username)[0])),
                            status=201,
                            mimetype='application/json')
        except KeyError as e:
            return Response(response=json.dumps({"error": "A value for {0} in the body was not included. "
                                                          "Please resubmit your request".format(e)}),
                            status=400,
                            mimetype='application/json')
        except sqlalchemy.exc.IntegrityError:
            return Response(response=json.dumps({"error": "A user with the username '{0}' already exists. "
                                                          "Please resubmit your request".format(username)}),
                            status=400,
                            mimetype='application/json')
        except Exception as e:
            logging.exception(e)
            return Response(response=json.dumps({"error": "An error occurred while creating the user. Please check "
                                                          "the logs."}),
                            status=500,
                            mimetype='application/json')


@api.route("/<string:user_name>")
class GetUser(Resource):
    @api.doc(
        "Get metadata for a user in the vault",
    )
    @api.response(200, 'Success', user_model)
    @api.response(404, 'No User Found')
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self, user_name):
        result = get_user(user_name)
        return Response(response=json.dumps([parse_to_user(r) for r in result]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')

    @api.doc(
        "Delete a user from the vault",
    )
    @api.response(204, 'User Deleted')
    @api.response(404, 'No User Found')
    @api.doc(security="basicAuth")
    @auth.login_required
    def delete(self, user_name):
        old_user = get_user(user_name)
        if len(old_user) == 0:
            return Response(status=404,
                            mimetype='application/json')

        db_session.execute(text(
            "CALL usp_DeleteUserByUsername(:userName);"),
            {"userName": user_name}
        )

        db_session.commit()

        return Response(status=204,
                        mimetype='application/json')

    @api.doc(
        "Update a user's details in the vault",
    )
    @api.response(200, 'Details Updated')
    @api.response(404, 'No User Found')
    @api.doc(security="basicAuth")
    @api.expect(user_model_update)
    @auth.login_required
    def patch(self, user_name):
        old_user = get_user(user_name)
        if len(old_user) == 0:
            return Response(status=404,
                            mimetype='application/json')

        json_data = request.get_json(force=True)
        if 'password' in json_data:
            password_text = json_data['password']
            password_bytes = password_text.encode('utf-8')
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt)
            db_session.execute(text(
                "Update vault.Users SET Password = :password where UserName = :username"), {
                "username": user_name,
                "password": password_hash
            })
            db_session.commit()
        if 'policies' in json_data:
            policies = str(json_data['policies']).split(",")
            active_policies = get_policies()
            for p in policies:
                if p in list(active_policies.keys()):
                    db_session.execute(text("Replace into vault.UserPermissions (UserId, PermissionPolicyId) VALUES ("
                                       ":userId, :permissionId)"),
                                       {
                                           "userId": old_user[0][0],
                                           "permissionId": active_policies[p]
                                       })
            if json_data['policies'] == '':
                db_session.execute(text("Delete from vault.UserPermissions where UserId = :userId;"),
                                   {
                                       "userId": old_user[0][0]
                                   })
        db_session.commit()
        return Response(response=json.dumps(parse_to_user(get_user(user_name)[0])),
                        status=200,
                        mimetype='application/json')
