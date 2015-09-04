import os

from flask import Flask
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from stevedore import (
    extension,
    driver,
    named,
)

from  . import config
from .models import db
from  . import views
from . import ext
from . import identity

def app_factory():
    app = Flask('pg-discuss', static_folder=None)

    # Load default config values from pg_discuss.config module
    app.config.from_object(config)
    # Load custom config from user-defined PG_DISCUSS_SETTINGS_FILE
    app.config.from_pyfile(os.environ['PG_DISCUSS_SETTINGS_FILE'])

    db.init_app(app)
    app.manager = Manager(app)
    app.migrate = Migrate(app, db)

    ## Use stevedore to load drivers/extensions.
    # Discover all drivers/extensions, but do not load any.
    # Used for logging found extensions.
    app.ext_mgr_all = extension.ExtensionManager(namespace='pg_discuss.ext')

    ## Load configured IdentityPolicy driver
    app.identity_policy_loader = driver.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_IDENTITY_POLICY'],
    )
    # Iniatialize IdentityPolicyManager with configured IdentityManager
    app.identity_policy_mgr = identity.IdentityPolicyManager(
        app,
        app.identity_policy_loader.driver,
    )

    ## Load configured CommentRenderer driver
    app.comment_renderer_loader = driver.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_COMMENT_RENDERER'],
    )
    app.comment_renderer = app.comment_renderer_loader.driver()

    ## Load configured JSONEncoder driver
    app.json_encoder_loader = driver.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_JSON_ENCODER'],
    )
    app.json_encoder = app.json_encoder_loader.driver

    # Exempt public read-only views from IdentityPolicy
    app.identity_policy_mgr.exempt(views.fetch)
    app.identity_policy_mgr.exempt(views.view)

    # Default routes. Other routes must be added through App extensions.
    # Default routes are set up before app extensions are loaded so extensions
    # can introspect/modify view functions.
    app.route('/threads/<string:thread_client_id>/comments', methods=['GET'])(views.fetch)
    app.route('/threads/<string:thread_client_id>/comments', methods=['POST'])(views.new)
    app.route('/comments/<int:comment_id>', methods=['GET'])(views.view)
    app.route('/comments/<int:comment_id>', methods=['PATCH'])(views.edit)
    app.route('/comments/<int:comment_id>', methods=['DELETE'])(views.delete)

    # Load all extensions explicitly enabled via `ENABLE_EXT_*` parameters.
    app.ext_mgr = named.NamedExtensionManager(
        namespace='pg_discuss.ext',
        names=config.get_enabled_extensions(app.config),
        name_order=True,
        invoke_on_load=True,
        invoke_kwds={'app': app},
        on_load_failure_callback=ext.fail_on_ext_load,
        propagate_map_exceptions=True,
    )

    app.manager.add_command('db', MigrateCommand)

    return app
