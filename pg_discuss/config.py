"""Base configuration and configuration helper functions.

Defaults are appropriate for production use.

All connection parameters and secrets should be read from the environment.
"""
import os
import logging

#: Python recursion limit. This determines at what level of comment nesting
#: the JSON encoder will hit "RuntimeError: maximum recursion depth exceeded".
PYTHON_RECURSION_LIMIT = 30000

# Extension settings
#: Configuration parameters of the form `ENABLE_EXT_*` are special:
#: the set of these parameters are parsed into a list of extension entrypoints
#: to be enabled.  The part of the string after the prefix `ENABLE_EXT_` is
#: taken to be the name of an extension entrypoint in all caps. All entrypoints
#: are required to have lowercase names.
#:
#: Example: if `ENABLE_EXT_FOO=True`, the extension with entrypoint name `foo`
#: will be enabled.
#:
#: The purpose of these "magic" config parameters is:
#:
#: - to allow atomic enablement of extensions without knowing apriori all of
#:   the entrypoint names.
#: - to avoid importing extensions that are not enabled. It is possible for
#:   extensions to "self-enable" ala stevedore's `EnabledExtensionManager`,
#:   which requires that extensions be imported before checking to see if they
#:   are enabled.
#: - to avoid having to list all extensions in a comma-separated string, which
#:   complicates atomic enabling and disabling of extensions.
#
# See the `get_enabled_extensions` in this module for parsing details.
ENABLE_EXT_BLESSED_ADMIN = True
#:
ENABLE_EXT_BLESSED_CSRF_TOKEN = True
#:
ENABLE_EXT_BLESSED_CSRF_HEADER = True
#:
ENABLE_EXT_BLESSED_ROUTE_LIST = True
#:
ENABLE_EXT_BLESSED_ARCHIVE_COMMENT_VERSIONS = True
#:
ENABLE_EXT_BLESSED_VALIDATE_COMMENT_LEN = True
#:
ENABLE_EXT_BLESSED_ISSO_CLIENT_SHIM = True
#:
ENABLE_EXT_BLESSED_CORS = True
#:
ENABLE_EXT_BLESSED_CAPTURE_AUTHOR = True
#:
ENABLE_EXT_BLESSED_CAPTURE_EMAIL = True
#:
ENABLE_EXT_BLESSED_CAPTURE_WEBSITE = True
#:
ENABLE_EXT_BLESSED_CAPTURE_REMOTE_ADDR = True
#:
ENABLE_EXT_BLESSED_VOTING = True
#:
ENABLE_EXT_BLESSED_MODERATION = False
#:
ENABLE_EXT_BLESSED_MOD_EMAIL = False
#:
ENABLE_EXT_BLESSED_PROFILER = False
#:
ENABLE_EXT_BLESSED_DOZER = False

#: Optional: Order extensions using comma-separated list of extension names.
#: It is generally discouraged to write order-dependent extensions, but
#: is required in some cases.
#: It is not necessary to list all extensions, only those that are required
#: to be ordered. See `config:sorted_ext_names` for sort logic details.
EXT_ORDER = (
    'blessed_voting,'
    'blessed_admin,'
    'blessed_moderation,'
    'blessed_isso_client_shim,'
)

# Driver settings
#: Comment renderer driver to use (as a setuptools entrypoint name)
DRIVER_COMMENT_RENDERER = 'blessed_markdown_renderer'
#: JSON encoder driver to use (as a setuptools entrypoint name)
DRIVER_JSON_ENCODER = 'blessed_unix_time_json_encoder'
#: Identity driver to use (as a setuptools entrypoint name)
DRIVER_IDENTITY_POLICY = 'blessed_auth_tkt_identity_policy'

# Session settings
#: Expiration of a permanent sesison in seconds.
PERMANENT_SESSION_LIFETIME = 3600
#: Default cookies to use `Secure` flag to avoid leaking unique machine
#: identifiers over the network. Non-HTTPS deployments must explicitly disable.
#: https://www.owasp.org/index.php/SecureFlag
SESSION_COOKIE_SECURE = True
#: Default cookies to use `HttpOnly` flag to deny client side scripts access
#: to the cookie. Defaults to True in Flask, but we want to be explicit.
#: https://www.owasp.org/index.php/HttpOnly
SESSION_COOKIE_HTTP_ONLY = True

# Log settings
#: Log level
LOGLEVEL = logging.INFO

#: List of parameters which should not be logged. This should list any
#: configuration parameters which include secrets, such as SECRET_KEY,
#: or the database connection string which may have a password.
DO_NOT_LOG_VARS = [
    'SECRET_KEY',
    'SQLALCHEMY_DATABASE_URI',
]

# Connection parameters and secrets
#: Database connection string.
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
#: Secret key used for cookie signing.
SECRET_KEY = os.environ.get('SECRET_KEY')
#: Name and port number of the server.
#: SERVER_NAME is required by some extensions that need to build absolute urls
#: in the context of emails, etc.
SERVER_NAME = os.environ.get('SERVER_NAME')

#: List of allowed origins (origins where widget will be embedded)
#: http://www.w3.org/TR/cors/
#: Attempt to read CORS_ORIGIN from environment as a comma-separated list of
#: origins.
CORS_ORIGINS = []
cors_origins_from_env = os.environ.get('CORS_ORIGINS')
if cors_origins_from_env:
    CORS_ORIGINS = cors_origins_from_env.split(',')

#: List of headers that client is allowed to read.
CORS_EXPOSE_HEADERS = ['Date', 'X-Set-Cookie']


def get_enabled_extensions(config):
    """Get the list of extension entrypoint names where `ENABLE_EXT_*` is True.
    """
    prefix = 'ENABLE_EXT_'

    enable_ext_vars = [k for k in config.keys() if k.startswith(prefix)]

    ext_names = [k[len(prefix):].lower() for k in enable_ext_vars if config[k]]

    return sorted_ext_names(config, ext_names)


def sorted_ext_names(config, ext_names):
    """Sort extensions if `EXT_ORDER` is specified. Extensions not listed in
    `EXT_ORDER` will be appended to the end of the list in an arbitrary order.
    """
    ext_order = [e.strip() for e in config['EXT_ORDER'].split(',')]

    def sort_key(ext_name):
        try:
            return ext_order.index(ext_name)
        except ValueError:
            # If `ext_name` is not in the sort list, it has a sort value of
            # positive infinity (last).
            return float('inf')

    return sorted(ext_names, key=sort_key)
