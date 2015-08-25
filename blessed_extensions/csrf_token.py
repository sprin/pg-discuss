"""
CSRF token generation, validation, and middleware.

Forked from flask_wtf.csrf:
https://github.com/lepture/flask-wtf/blob/HEAD/flask_wtf/csrf.py
"""

import os
import hmac
import hashlib
import time
from flask import current_app, session, request, abort
from werkzeug.security import safe_str_cmp
from pg_discuss._compat import (
    to_bytes,
    urlparse,
)
from pg_discuss.extension_base import AppExtBase

__all__ = ('generate_csrf', 'validate_csrf', 'CsrfProtect')


def generate_csrf(secret_key=None, time_limit=None):
    """Generate csrf token code.
    :param secret_key: A secret key for mixing in the token,
                       default is Flask.secret_key.
    :param time_limit: Token valid in the time limit,
                       default is 3600s.
    """
    if not secret_key:
        secret_key = current_app.config['SECRET_KEY']
        if not secret_key:
            raise ValueError('Must provide secret_key to use csrf.')

    if time_limit is None:
        time_limit = current_app.config['CSRF_TOKEN_TIME_LIMIT']

    if 'csrf_token' not in session:
        session['csrf_token'] = hashlib.sha1(os.urandom(64)).hexdigest()

    if time_limit:
        expires = int(time.time() + time_limit)
        csrf_build = '%s%s' % (session['csrf_token'], expires)
    else:
        expires = ''
        csrf_build = session['csrf_token']

    hmac_csrf = hmac.new(
        to_bytes(secret_key),
        to_bytes(csrf_build),
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
        time_limit = current_app.config['CSRF_TOKEN_TIME_LIMIT']

    if time_limit:
        try:
            expires = int(expires)
        except ValueError:
            return False

        now = int(time.time())
        if now > expires:
            return False

    if not secret_key:
        secret_key = current_app.config['SECRET_KEY']
        if not secret_key:
            raise ValueError('Must provide secret_key to use csrf.')

    if 'csrf_token' not in session:
        return False

    csrf_build = '%s%s' % (session['csrf_token'], expires)
    hmac_compare = hmac.new(
        to_bytes(secret_key),
        to_bytes(csrf_build),
        digestmod=hashlib.sha1
    ).hexdigest()

    return safe_str_cmp(hmac_compare, hmac_csrf)

def get_csrf_token():
    return generate_csrf()

class CsrfTokenExt(AppExtBase):
    """Enable csrf protect for Flask.
    Register it with::
        app = Flask(__name__)
        CsrfTokenExt(app)
    And in the templates, add the token input::
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    If you need to send the token via AJAX, and there is no form::
        <meta name="csrf_token" content="{{ csrf_token() }}" />
    You can grab the csrf token with JavaScript, and send the token together.
    """

    def init_app(self, app):
        self._app = app

        app.route('/csrftoken', methods=['GET'])(get_csrf_token)

        if not app.config['CSRF_TOKEN_CHECK_DEFAULT']:
            return

        @app.before_request
        def _csrf_protect():
            # many things come from django.middleware.csrf
            if request.method in app.config['CSRF_TOKEN_EXEMPT_METHODS']:
                return

            if self._exempt_views:
                if not request.endpoint:
                    return

                view = app.view_functions.get(request.endpoint)
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
            csrf_token = request.headers.get(header_name)
            if csrf_token:
                return csrf_token
        return None

    def protect(self):
        if request.method in self._app.config['CSRF_TOKEN_EXEMPT_METHODS']:
            return

        if not validate_csrf(self._get_csrf_token()):
            reason = 'CSRF token missing or incorrect.'
            return self._error_response(reason)

        if request.is_secure and self._app.config['CSRF_SSL_STRICT']:
            if not request.referrer:
                reason = 'Referrer checking failed - no Referrer.'
                return self._error_response(reason)

            good_referrer = 'https://%s/' % request.host
            if not same_origin(request.referrer, good_referrer):
                reason = 'Referrer checking failed - origin does not match.'
                return self._error_response(reason)

        request.csrf_token_valid = True  # mark this request is csrf valid

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
        self._exempt_views.add(view_location)
        return view

    def _error_response(self, reason):
        return abort(403, reason)


def same_origin(current_uri, compare_uri):
    parsed_uri = urlparse(current_uri)
    parsed_compare = urlparse(compare_uri)

    if parsed_uri.scheme != parsed_compare.scheme:
        return False

    if parsed_uri.hostname != parsed_compare.hostname:
        return False

    if parsed_uri.port != parsed_compare.port:
        return False
    return True
