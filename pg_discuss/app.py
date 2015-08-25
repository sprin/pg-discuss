import os

from flask import Flask
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from stevedore import (
    extension,
    named,
)

from  . import config
from .models import db
from  . import views
from . import forms
from .json_mimetype import CheckJsonMimetype
from .json import CustomJSONEncoder
from .management import ListRoutes

def app_factory():
    app = Flask('pg-discuss')

    # Load default config values from pg_discuss.config module
    app.config.from_object(config)
    # Load custom config from user-defined PG_DISCUSS_SETTINGS_FILE
    app.config.from_pyfile(os.environ['PG_DISCUSS_SETTINGS_FILE'])

    app.comment_text_validator_factory = (
        forms.default_comment_text_validator_factory
    )
    app.json_mimetype = CheckJsonMimetype(app)
    db.init_app(app)
    app.manager = Manager(app)
    app.migrate = Migrate(app, db)
    app.json_encoder = CustomJSONEncoder

    ## Use stevedore to load extensions.
    # Discover all extensions, but do not load any.
    # Used for logging found extensions.
    app.ext_mgr_all = extension.ExtensionManager(
        namespace='pg_discuss.ext'
    )
    # Load all extensions explicitly enabled via `ENABLE_EXT_*` parameters.
    app.ext_mgr = named.NamedExtensionManager(
        namespace='pg_discuss.ext',
        names=config.get_enabled_extensions(app.config),
        invoke_on_load=True,
        invoke_kwds={'app': app},
    )

    app.manager.add_command('db', MigrateCommand)
    app.manager.add_command('list_routes', ListRoutes())

    # Default routes. Other routes must be added through App extensions.
    app.route('/', methods=['GET'])(views.fetch)
    app.route('/new', methods=['POST'])(views.new)
    app.route('/id/<int:comment_id>', methods=['GET'])(views.view)

    return app
