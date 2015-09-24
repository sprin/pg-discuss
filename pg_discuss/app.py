import os

import flask
import flask_login
import flask_migrate
import flask_script
import stevedore

from . import _compat
from . import auth_forms
from . import config
from . import db
from . import ext
from . import identity
from . import models
from . import views

# Use psycopg2cffi if PYPY
if _compat.PYPY: # pragma: no cover
    from psycopg2cffi import compat as pg2cfficompat

def app_factory():
    if _compat.PYPY: # pragma: no cover
        pg2cfficompat.register()
    app = flask.Flask('pg-discuss', static_folder=None,
                template_folder='pg_discuss/templates')

    # Load default config values from pg_discuss.config module
    app.config.from_object(config)
    # Load custom config from user-defined PG_DISCUSS_SETTINGS_FILE
    app.config.from_pyfile(os.environ['PG_DISCUSS_SETTINGS_FILE'])

    db.init_app(app)
    app.manager = flask_script.Manager(app)
    app.migrate = flask_migrate.Migrate(app, db)
    # Login manager for Admin users.
    app.admin_login_manager = flask_login.LoginManager(app)

    def load_user(user_id):
        return db.session.query(models.AdminUser).get(user_id)
    app.admin_login_manager.user_loader(load_user)

    ## Use stevedore to load drivers/extensions.
    # Discover all drivers/extensions, but do not load any.
    # Used for logging found extensions.
    app.ext_mgr_all = stevedore.ExtensionManager(
        namespace='pg_discuss.ext')

    ## Load configured IdentityPolicy driver
    app.identity_policy_loader = stevedore.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_IDENTITY_POLICY'],
    )
    # Iniatialize IdentityPolicyManager with configured IdentityManager
    app.identity_policy_mgr = identity.IdentityPolicyManager(
        app,
        app.identity_policy_loader.driver,
    )

    ## Load configured CommentRenderer driver
    app.comment_renderer_loader = stevedore.DriverManager(
        namespace='pg_discuss.ext',
        name=app.config['DRIVER_COMMENT_RENDERER'],
    )
    app.comment_renderer = app.comment_renderer_loader.driver()

    ## Load configured JSONEncoder driver
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
    app.route('/threads/<string:thread_client_id>/comments', methods=['GET'])(views.fetch)
    app.route('/threads/<string:thread_client_id>/comments', methods=['POST'])(views.new)
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
    # Run the `init_app` hooks.
    ext.exec_init_app(app)

    app.manager.add_command('db', flask_migrate.MigrateCommand)
    app.manager.add_command('createadminuser', auth_forms.CreateAdminUser)

    return app
