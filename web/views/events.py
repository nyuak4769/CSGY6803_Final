import json

from webauth import auth
from sqlalchemy import text, select
from flask import Blueprint, jsonify, Response
from database import db_session
from flask_restx import fields, Resource, Namespace

api = Namespace('events', "Event related operations")

event_model = api.model('EventModel', {
    'Id': fields.String(description='ID of the Event'),
    'EventCode': fields.String(description='Event Code for the Event'),
    'Timestamp': fields.String(description='Timestamp the Event'),
    'SecretId': fields.String(description='ID of the secret contained in the Event'),
})

def parse_to_event(row):
    return {
        'Id': row[0],
        'EventCode': row[1],
        'Timestamp': row[2].isoformat(),
        'SecretId': row[3]
    }


@api.route("/")
class GetAllEvents(Resource):
    @api.doc(
        "Get All Events",
        responses={
            200: "Event Data Found",
            404: "No Events Found",
        },
    )
    @api.response(200, "Event Data Found", event_model)
    @api.response(400, "No Events Found")
    @api.doc(security="basicAuth")
    @auth.login_required
    def get(self):
        from views.secrets import get_secrets_for_user
        result = db_session.execute(text("Select * from vault.v_SecretEvents limit 100;")).all()
        secrets = list(i[0] for i in get_secrets_for_user(auth.current_user()))
        filtered_events = list(i for i in result if i[3] in secrets)
        return Response(response=json.dumps([parse_to_event(r) for r in filtered_events]),
                        status=(200 if len(result) > 0 else 404),
                        mimetype='application/json')
