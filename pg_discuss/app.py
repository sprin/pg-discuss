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
from .csrf_token import CsrfProtectWithToken
from .csrf_header import CsrfProtectWithHeader
from .json_mimetype import CheckJsonMimetype
from .json import CustomJSONEncoder

def app_factory():
    app = Flask('pg-discuss')

    # Load default config values from pg_discuss.config module
    app.config.from_object(config)
    # Load custom config from user-defined PG_DISCUSS_SETTINGS_FILE
    app.config.from_pyfile(os.environ['PG_DISCUSS_SETTINGS_FILE'])

    # Set up logging
    app.logger.setLevel(app.config['LOGLEVEL'])

    # Log configuration parameters
    app.logger.info('Configuration parameters:\n{}'.format(
        '\n'.join([k + '=' + str(v) for k, v in
                   sorted(app.config.items())
                   if k not in config.DO_NOT_LOG_VARS])))

    app.comment_text_validator_factory = (
        forms.default_comment_text_validator_factory
    )
    app.csrf_token = CsrfProtectWithToken(app)
    app.csrf_header = CsrfProtectWithHeader(app)
    app.json_mimetype = CheckJsonMimetype(app)
    db.init_app(app)
    app.manager = Manager(app)
    app.migrate = Migrate(app, db)
    app.json_encoder = CustomJSONEncoder

    ## Use stevedore to load extensions.
    # Discover and log all extensions (but do not load any)
    app.ext_mgr = extension.ExtensionManager(
        namespace='pg_discuss.ext'
    )
    app.logger.info('Found extensions:\n{}'.format(
        '\n'.join([e.name for e in app.ext_mgr.extensions])))

    # Load all extensions explicitly enabled via `ENABLE_EXT_*` parameters.
    app.ext_mgr = named.NamedExtensionManager(
        namespace='pg_discuss.ext',
        names=config.get_enabled_extensions(app.config),
        invoke_on_load=True,
        invoke_kwds={'app': app},
    )
    app.logger.info('Enabled extensions:\n{}'.format(
        '\n'.join([e.name for e in app.ext_mgr.extensions])))

    app.manager.add_command('db', MigrateCommand)

    # Default routes. Other routes must be added through App extensions.
    app.route('/', methods=['GET'])(views.fetch)
    app.route('/new', methods=['POST'])(views.new)
    app.route('/id/<int:comment_id>', methods=['GET'])(views.view)
    app.route('/csrftoken', methods=['GET'])(views.csrftoken)

    return app
