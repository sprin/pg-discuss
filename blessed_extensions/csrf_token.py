import hashlib
import hmac
import os
import time

import flask
import werkzeug.security

from pg_discuss import _compat
from pg_discuss import ext

#: Protect all views from CSRF by verifying token by default.
CSRF_TOKEN_CHECK_DEFAULT = True
#: Expiration of a CSRF token in seconds.
CSRF_TOKEN_TIME_LIMIT = 3600
#: Headers in which to submit CSRF token.
CSRF_TOKEN_HEADERS = ['X-CSRF-Token']
#: Exempt a list of HTTP methods from the check (read-only methods should be
#: exempted).
CSRF_TOKEN_EXEMPT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
CSRF_SSL_STRICT = True


class CsrfTokenExt(ext.AppExtBase):
    """
    CSRF token extension.

    Forked from flask_wtf.csrf:
    https://github.com/lepture/flask-wtf/blob/HEAD/flask_wtf/csrf.py

    Verifies the token present in the cookie against a token sent in the
    `X-CSRF-Token` HTTP header.
    """
    def init_app(self, app):
        self._app = app
        self._exempt_views = []
        app.config.setdefault('CSRF_TOKEN_CHECK_DEFAULT',
                              CSRF_TOKEN_CHECK_DEFAULT)
        app.config.setdefault('CSRF_TOKEN_TIME_LIMIT', CSRF_TOKEN_TIME_LIMIT)
        app.config.setdefault('CSRF_TOKEN_HEADERS', CSRF_TOKEN_HEADERS)
        app.config.setdefault('CSRF_TOKEN_EXEMPT_METHODS',
                              CSRF_TOKEN_EXEMPT_METHODS)
        app.config.setdefault('CSRF_SSL_STRICT', CSRF_SSL_STRICT)

        app.route('/csrftoken', methods=['GET'])(get_csrf_token)

        if not app.config['CSRF_TOKEN_CHECK_DEFAULT']:
            return

        @app.before_request
        def _csrf_protect():
            # many things come from django.middleware.csrf
            if flask.request.method in app.config['CSRF_TOKEN_EXEMPT_METHODS']:
                return

            if self._exempt_views:
                if not flask.request.endpoint:
                    return

                view = app.view_functions.get(flask.request.endpoint)
                if not view:
                    return

                dest = '%s.%s' % (view.__module__, view.__name__)
                if dest in self._exempt_views:
                    return

            self.protect()

    def _get_csrf_token(self):
        """Extract CSRF token from headers.
        """
        for header_name in self._app.config['CSRF_TOKEN_HEADERS']:
            csrf_token = flask.request.headers.get(header_name)
            if csrf_token:
                return csrf_token
        return None

    def protect(self):
        if (
            flask.request.method
            in self._app.config['CSRF_TOKEN_EXEMPT_METHODS']
        ):
            return

        if not validate_csrf(self._get_csrf_token()):
            reason = 'CSRF token missing or incorrect.'
            return self._error_response(reason)

        if flask.request.is_secure and self._app.config['CSRF_SSL_STRICT']:
            if not flask.request.referrer:
                reason = 'Referrer checking failed - no Referrer.'
                return self._error_response(reason)

            good_referrer = 'https://%s/' % flask.request.host
            if not same_origin(flask.request.referrer, good_referrer):
                reason = 'Referrer checking failed - origin does not match.'
                return self._error_response(reason)

        # Mark the request as having a valid CSRF token
        flask.request.csrf_token_valid = True

    def exempt(self, view):
        """A decorator that can exclude a view from csrf protection.
        Remember to put the decorator above the `route`::
            csrf = CsrfProtect(app)
            @csrf.exempt
            @app.route('/some-view', methods=['POST'])
            def some_view():
                return
        """
        view_location = '%s.%s' % (view.__module__, view.__name__)
        self._exempt_views.append(view_location)
        return view

    def _error_response(self, reason):
        return flask.abort(403, reason)


def generate_csrf(secret_key=None, time_limit=None):
    """Generate csrf token code.
    :param secret_key: A secret key for mixing in the token,
                       default is Flask.secret_key.
    :param time_limit: Token valid in the time limit,
                       default is 3600s.
    """
    if not secret_key:
        secret_key = flask.current_app.config['SECRET_KEY']
        if not secret_key:
            raise ValueError('Must provide secret_key to use csrf.')

    if time_limit is None:
        time_limit = flask.current_app.config['CSRF_TOKEN_TIME_LIMIT']

    if 'csrf_token' not in flask.session:
        flask.session['csrf_token'] = hashlib.sha1(os.urandom(64)).hexdigest()

    if time_limit:
        expires = int(time.time() + time_limit)
        csrf_build = '%s%s' % (flask.session['csrf_token'], expires)
    else:
        expires = ''
        csrf_build = flask.session['csrf_token']

    hmac_csrf = hmac.new(
        _compat.to_bytes(secret_key),
        _compat.to_bytes(csrf_build),
        digestmod=hashlib.sha1
    ).hexdigest()
    return '%s##%s' % (expires, hmac_csrf)


def validate_csrf(data, secret_key=None, time_limit=None):
    """Check if the given data is a valid csrf token.
    :param data: The csrf token value to be checked.
    :param secret_key: A secret key for mixing in the token,
                       default is Flask.secret_key.
    :param time_limit: Check if the csrf token is expired.
                       default is True.
    """
    if not data or '##' not in data:
        return False

    expires, hmac_csrf = data.split('##', 1)

    if time_limit is None:
        time_limit = flask.current_app.config['CSRF_TOKEN_TIME_LIMIT']

    if time_limit:
        try:
            expires = int(expires)
        except ValueError:
            return False

        now = int(time.time())
        if now > expires:
            return False

    if not secret_key:
        secret_key = flask.current_app.config['SECRET_KEY']
        if not secret_key:
            raise ValueError('Must provide secret_key to use csrf.')

    if 'csrf_token' not in flask.session:
        return False

    csrf_build = '%s%s' % (flask.session['csrf_token'], expires)
    hmac_compare = hmac.new(
        _compat.to_bytes(secret_key),
        _compat.to_bytes(csrf_build),
        digestmod=hashlib.sha1
    ).hexdigest()

    return werkzeug.security.safe_str_cmp(hmac_compare, hmac_csrf)


def get_csrf_token():
    return generate_csrf()


def same_origin(current_uri, compare_uri):
    parsed_uri = _compat.urlparse(current_uri)
    parsed_compare = _compat.urlparse(compare_uri)

    if parsed_uri.scheme != parsed_compare.scheme:
        return False

    if parsed_uri.hostname != parsed_compare.hostname:
        return False

    if parsed_uri.port != parsed_compare.port:
        return False
    return True
