from flask import (
    abort,
    request,
)

from pg_discuss.ext import AppExtBase

class CsrfHeaderExt(AppExtBase):
    """Middleware to verify the request is an XHR request.
    This assumes that all, or most, data-modifying views are intended to handle
    XHR requests.

    Register it with::
        app = Flask(__name__)
        CsrfHeaderExt(app)

    Note that Content-Type checking alone does not necessarily protect against
    CSRF if browsers implement "HTML JSON form submission":
    http://www.w3.org/TR/html-json-forms/

    However, when the X-Requested-With header is checked, this is considered to
    be adequate protection by some:
    http://security.stackexchange.com/q/23371

    The CsrfProtectWithToken middleware (enabled by default) must be enabled for
    full token-based CSRF protection.
    """

    def init_app(self, app):
        self._app = app

        app.config.setdefault('CSRF_HEADER_ENABLED', True)
        app.config.setdefault('CSRF_HEADER_CHECK_DEFAULT', True)
        app.config.setdefault('CSRF_HEADER_EXEMPT_METHODS',
                              ['GET', 'HEAD', 'OPTIONS', 'TRACE'])

        if not app.config['CSRF_HEADER_CHECK_DEFAULT']:
            return

        @app.before_request
        def _csrf_protect():
            # many things come from django.middleware.csrf
            if request.method in app.config['CSRF_HEADER_EXEMPT_METHODS']:
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

    def protect(self):
        if self._app.config['CSRF_HEADER_ENABLED']:
            if not request.is_xhr:
                reason = (
                    'XHR checking failed - X-Requested-With not set '
                    'to XMLHttpRequest'
                )
                return self._error_response(reason)
        request.csrf_header_valid = True

    def exempt(self, view):
        """A decorator that can exclude a view from XHR checking.
        Remember to put the decorator above the `route`::
            csrf_header = CsrfProtectWithHeader(app)
            @csrf_header.exempt
            @app.route('/some-view', methods=['POST'])
            def some_view():
                return
        """
        view_location = '%s.%s' % (view.__module__, view.__name__)
        self._exempt_views.add(view_location)
        return view

    def _error_response(self, reason):
        return abort(403, reason)
