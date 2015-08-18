"""Base configuration.

Defaults are appropriate for production use.

All connection parameters and secrets should be read from the environment.
"""
import os

# Connection parameters and secrets
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SECRET_KEY = os.environ['SECRET_KEY']

# Other configuration defaults
CSRF_ENABLED = True
CSRF_CHECK_DEFAULT = True
CSRF_SSL_STRICT = True
CSRF_TIME_LIMIT = 3600
CSRF_HEADERS = ['X-CSRF-Token']
CSRF_EXEMPT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
XHR_CHECK_ENABLED = True
XHR_CHECK_DEFAULT = True
XHR_CHECK_EXEMPT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
