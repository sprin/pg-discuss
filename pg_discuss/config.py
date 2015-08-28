"""Base configuration and configuration helper functions.

Defaults are appropriate for production use.

All connection parameters and secrets should be read from the environment.
"""
import os

## Extension settings
# Configuration parameters of the form `ENABLE_EXT_*` are special:
# the set of these parameters are parsed into a list of extension entrypoints to
# be enabled.  The part of the string after the prefix `ENABLE_EXT_` is taken to
# be the name of an extension entrypoint in all caps. All entrypoints are
# required to have lowercase names.
#
# Example: if `ENABLED_EXT_FOO=True`, the extension with entrypoint name `foo`
# will be enabled.
#
# The purpose of these "magic" config parameters is:
# - to allow atomic enablement of extensions without knowing apriori all of the
#   entrypoint names.
# - to avoid importing extensions that are not enabled. It is possible for
#   extensions to "self-enable" ala stevedore's `EnabledExtensionManager`, which
#   requires that extensions be imported before checking to see if they are
#   enabled.
# - to avoid having to list extensions in a comma-separated string, which
#   complicates atomic enabling and disabling of extensions.
#
# See the `get_enabled_extensions` in this module for parsing details.
ENABLE_EXT_BLESSED_EDIT_VIEW = True
ENABLE_EXT_BLESSED_DELETE_VIEW = True
ENABLE_EXT_BLESSED_CSRF_TOKEN = True
ENABLE_EXT_BLESSED_CSRF_HEADER = True
ENABLE_EXT_BLESSED_JSON_MIMETYPE = True
ENABLE_EXT_BLESSED_ROUTE_LIST = True
ENABLE_EXT_BLESSED_ARCHIVE_UPDATES = True
ENABLE_EXT_BLESSED_VALIDATE_COMMENT_LEN = True
ENABLE_EXT_BLESSED_ISSO_CLIENT_SHIM = True
ENABLE_EXT_BLESSED_CORS = True

# Optional: Order extensions using comma-separated list of extension names.
# It is generally discouraged to write order-dependent extensions, but it may
# be required in some cases.
# It is not necessary to list all extensions, only those that are required
# to be ordered. See `config:sorted_ext_names` for sort logic details.
EXT_ORDER = ''

## Driver settings
DRIVER_JSON_ENCODER = 'blessed_iso_date_json_encoder'

## Log settings
LOGLEVEL = 'INFO'

# List of parameters which should not be logged. This should list any
# configuration parameters which include secrets, such as SECRET_KEY,
# or the database connection string which may have a password.
DO_NOT_LOG_VARS = [
    'SECRET_KEY',
    'SQLALCHEMY_DATABASE_URI',
]

## Connection parameters and secrets
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SECRET_KEY = os.environ['SECRET_KEY']

# Comment defaults
MIN_COMMENT_LENGTH = 3
MAX_COMMENT_LENGTH = 65535

# CORS: List of allowed origins (origins where widget will be embedded)
# http://www.w3.org/TR/cors/
CORS_ORIGINS=[]

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
