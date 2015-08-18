import os

from flask import Flask
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from pg_discuss import config
from pg_discuss.models import db
from pg_discuss import views
from pg_discuss.csrf import CsrfProtect
from pg_discuss.xhr import XhrCheck
from pg_discuss.json import CustomJSONEncoder

def app_factory():
    app = Flask('pg-discuss')

    # Load default config values from pg_discuss.config module
    app.config.from_object(config)
    # Load custom config from user-defined PG_DISCUSS_SETTINGS_FILE
    app.config.from_pyfile(os.environ['PG_DISCUSS_SETTINGS_FILE'])

    app.csrf = CsrfProtect(app)
    app.xhr = XhrCheck(app)
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
