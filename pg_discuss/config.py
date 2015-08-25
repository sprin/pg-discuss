"""Base configuration and configuration helper functions.

Defaults are appropriate for production use.

All connection parameters and secrets should be read from the environment.
"""
import os

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

LOGLEVEL = 'INFO'

# Connection parameters and secrets
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SECRET_KEY = os.environ['SECRET_KEY']

# Comment defaults
MIN_COMMENT_LENGTH = 3
MAX_COMMENT_LENGTH = 65535

# List of parameters which should not be logged. This should list any
# configuration parameters which include secrets, such as SECRET_KEY,
# or the database connection string which may have a password.
DO_NOT_LOG_VARS = [
    'SECRET_KEY',
    'SQLALCHEMY_DATABASE_URI',
]

def get_enabled_extensions(config):
    """Get the list of extension entrypoint names where `ENABLE_EXT_*` is True.
    """
    prefix = 'ENABLE_EXT_'

    enable_ext_vars = [k for k in config.keys() if k.startswith(prefix)]

    return [k[len(prefix):].lower() for k in enable_ext_vars if config[k]]
