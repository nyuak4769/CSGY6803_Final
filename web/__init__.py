import flask
from flask import Flask, session, g, render_template
from flask_restx import Api
from flask import Blueprint

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint,
          title='Vault as a Service API',
          version='1.0',
          description='A proof of concept vault service',
          )

from views import events
from views import secrets
from views import permission_policies
from views import rotation_policies

app.register_blueprint(blueprint)
api.add_namespace(events.api)
api.add_namespace(secrets.api)
api.add_namespace(permission_policies.api)
api.add_namespace(rotation_policies.api)


@app.route('/')
def do_redirect():
    return flask.redirect('/api/v1')


if __name__ == "__main__":
    app.run()