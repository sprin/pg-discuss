"""Base configuration.

Defaults are appropriate for production use.

All connection parameters and secrets should be read from the environment.
"""
import os

# Connection parameters and secrets
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SECRET_KEY = os.environ['SECRET_KEY']

# Security defaults
CSRF_TOKEN_ENABLED = True
CSRF_TOKEN_CHECK_DEFAULT = True
CSRF_TOKEN_TIME_LIMIT = 3600
CSRF_TOKEN_HEADERS = ['X-CSRF-Token']
CSRF_TOKEN_EXEMPT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
CSRF_SSL_STRICT = True
CSRF_HEADER_ENABLED = True
CSRF_HEADER_CHECK_DEFAULT = True
CSRF_HEADER_EXEMPT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
JSON_MIMETYPE_ENABLED = True
JSON_MIMETYPE_CHECK_DEFAULT = True
JSON_MIMETYPE_EXEMPT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']

# Comment defaults
MIN_COMMENT_LENGTH = 3
MAX_COMMENT_LENGTH = 65535
