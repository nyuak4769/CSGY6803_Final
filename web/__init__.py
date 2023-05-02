import logging

import flask
import sqlalchemy.exc
from flask import Flask, session, g, render_template
from flask_restx import Api
from flask import Blueprint
from database import db_session
from sqlalchemy import text

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False

authorizations = {
    "basicAuth": {
        "type": "basic"
    }
}

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint,
          title='Vault as a Service API',
          version='1.0',
          description='A proof of concept vault service',
          authorizations=authorizations
          )

from views import events
from views import secrets
from views import permission_policies
from views import rotation_policies
from views import users

app.register_blueprint(blueprint)
api.add_namespace(events.api)
api.add_namespace(secrets.api)
api.add_namespace(permission_policies.api)
api.add_namespace(rotation_policies.api)
api.add_namespace(users.api)

try:
    db_session.execute(text('SELECT 1'))
except sqlalchemy.exc.OperationalError:
    logging.error("Unable to connect to Database")
    exit(1)


@app.route('/')
def do_redirect():
    return flask.redirect('/api/v1')


if __name__ == "__main__":
    app.run()