"""Factory function for the WSGI application object.
"""
import os
import sys

import flask
import flask_login
import flask_migrate
import flask_script
import stevedore

from . import _compat
from . import auth_forms
from . import config
from . import ext
from . import identity
from . import models
from . import views
from .db import db

if _compat.PYPY:  # pragma: no cover
    from psycopg2cffi import compat as pg2cfficompat


def app_factory():
    """Factory function for the WSGI application object.

    Reads config, initializes Flask extensions that are part of the core,
    loads pg-config drivers and extensions, and configures core views.
    """
    # Use psycopg2cffi if PYPY
    if _compat.PYPY:  # pragma: no cover
        pg2cfficompat.register()

    # Flask application
    app = flask.Flask('pg-discuss')
    app.root_path = os.path.abspath(os.path.dirname(__file__))

    # Load default config values from pg_discuss.config module
    app.config.from_object(config)

    # Load custom config from user-defined PG_DISCUSS_SETTINGS_FILE
    custom_settings = os.environ.get('PG_DISCUSS_SETTINGS_FILE',
                                     '/opt/pg-discuss/local_settings.py')
    if custom_settings and os.path.isfile(custom_settings):
        app.config.from_pyfile(custom_settings)

    # Set the recursion limit
    sys.setrecursionlimit(app.config['PYTHON_RECURSION_LIMIT'])

    # Flask-SQLAlchemy
    db.init_app(app)

    # Flask-Migrate
    app.migrate = flask_migrate.Migrate(app, db)

    # Flask-Script
    app.script_manager = flask_script.Manager(app)
    app.script_manager.add_command('db', flask_migrate.MigrateCommand)
    app.script_manager.add_command('createadminuser',
                                   auth_forms.CreateAdminUser)

    # Flask-Login, for Admin users.
    app.admin_login_manager = flask_login.LoginManager(app)
    # Set up callback to load user objects`
    app.admin_login_manager.user_loader(
        lambda user_id: db.session.query(models.AdminUser).get(user_id))

    # Use stevedore to load drivers/extensions.
    # Discover all drivers/extensions, but do not load any.
    # Used for logging found extensions.
    app.ext_mgr_all = stevedore.ExtensionManager(namespace='pg_discuss.ext')

    # Load configured IdentityPolicy driver
    app.identity_policy_loader = stevedore.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_IDENTITY_POLICY'],
    )
    # Initialize IdentityPolicyManager with configured IdentityManager
    app.identity_policy_mgr = identity.IdentityPolicyManager(
        app,
        app.identity_policy_loader.driver,
    )

    # Load configured CommentRenderer driver
    app.comment_renderer_loader = stevedore.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_COMMENT_RENDERER'],
    )
    app.comment_renderer = app.comment_renderer_loader.driver(app)

    # Load configured JSONEncoder driver
    app.json_encoder_loader = stevedore.DriverManager(
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
    app.route('/threads/<thread_cid>/comments', methods=['GET'])(views.fetch)
    app.route('/threads/<thread_cid>/comments', methods=['POST'])(views.new)
    app.route('/comments/<int:comment_id>', methods=['GET'])(views.view)
    app.route('/comments/<int:comment_id>', methods=['PATCH'])(views.edit)
    app.route('/comments/<int:comment_id>', methods=['DELETE'])(views.delete)
    app.route('/login', methods=['GET', 'POST'])(views.admin_login)
    app.route('/logout', methods=['GET'])(views.admin_logout)

    # Load all extensions explicitly enabled via `ENABLE_EXT_*` parameters.
    app.ext_mgr = stevedore.NamedExtensionManager(
        namespace='pg_discuss.ext',
        names=config.get_enabled_extensions(app.config),
        name_order=True,
        invoke_on_load=True,
        invoke_kwds={'app': app},
        on_load_failure_callback=ext.fail_on_ext_load,
        propagate_map_exceptions=True,
    )
    # Create hook map
    app.hook_map = ext.get_hook_map(app.ext_mgr.extensions, ext.hook_classes())

    # Run the `init_app` hooks.
    ext.exec_init_app(app)

    # Add a route to the landing page at the root, '/'. Ignore if an extension
    # has already set up a route for the root.
    try:
        app.route('/', methods=['GET'])(views.landing)
    except:
        pass

    # Run request callbacks after request.
    @app.after_request
    def call_after_request_callbacks(response):
        for callback in getattr(flask.g, 'after_request_callbacks', ()):
            callback(response)
        return response

    return app
