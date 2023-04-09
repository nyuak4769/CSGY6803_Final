import json

from database import Event
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


@api.route("/")
class GetAllEvents(Resource):
    @api.doc(
        "Get All Events",
        responses={
            200: "Event Data Found",
            404: "No Events Found",
        },
    )
    @api.marshal_list_with(event_model)
    def get(self):
        r = db_session.execute(select(Event).from_statement(text("Select * from vault.Events;"))).scalars().all()
        return Response(response=json.dumps(jsonify([i.toDict() for i in r])),
                        status=(200 if len(r) > 0 else 404),
                        mimetype='application/json')


@api.route("/<string:secretId>")
class GetAllEvents(Resource):
    @api.doc(
        "Get Events for a Specific Secret ID",
        responses={
            200: "Event Data Found",
            404: "No Events Found",
        },
    )
    @api.marshal_list_with(event_model)
    def get(self, secretId):
        stmt = select(Event).from_statement(text("Select * from vault.Events where SecretId = :id;"))
        r = db_session.execute(stmt, {"id": secretId}).scalars().all()
        return Response(response=json.dumps([i.toDict() for i in r]),
                            status=(200 if len(r) > 0 else 404),
                            mimetype='application/json')
