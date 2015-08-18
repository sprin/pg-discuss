from flask import (
    Flask,
)
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from pg_discuss.config import Config
from pg_discuss.models import db
from pg_discuss import views
from pg_discuss.csrf import CsrfProtect
from pg_discuss.json import CustomJSONEncoder

def app_factory():
    app = Flask('pg-discuss')
    app.config.from_object(Config)
    CsrfProtect(app)
    db.init_app(app)
    app.manager = Manager(app)
    app.migrate = Migrate(app, db)
    app.json_encoder = CustomJSONEncoder

    app.manager.add_command('db', MigrateCommand)

    app.route('/', methods=['GET'])(views.fetch)
    app.route('/new', methods=['POST'])(views.new)
    app.route('/id/<int:id>', methods=['GET'])(views.view)
    app.route('/id/<int:id>', methods=['PUT'])(views.edit)
    app.route('/id/<int:id>', methods=['DELETE'])(views.delete)
    app.route('/csrftoken', methods=['GET'])(views.csrftoken)

    return app
