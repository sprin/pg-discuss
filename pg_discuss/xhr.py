from flask import (
    abort,
    request,
)

class XhrCheck(object):
    """Middleware to verify the request is an XHR request and that Content-Type
    header is set to 'application/json'. This assumes that all, or most,
    data-modifying views are intended to handle XHR requests.

    Register it with::
        app = Flask(__name__)
        XhrCheck(app)

    Note that Content-Type checking does not necessarily protect against CSRF if
    browsers implement "HTML JSON form submission":
    http://www.w3.org/TR/html-json-forms/

    The CsrfProtect middleware (enabled by default) must be enabled for full
    token-based CSRF protection.
    """

    def __init__(self, app=None):
        self._exempt_views = set()

        if app:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        if not app.config['XHR_CHECK_ENABLED']:
            return

        if not app.config['XHR_CHECK_DEFAULT']:
            return

        @app.before_request
        def _csrf_protect():
            # many things come from django.middleware.csrf
            if request.method in app.config['XHR_CHECK_EXEMPT_METHODS']:
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

            self.check()

    def check(self):
        if self._app.config['XHR_CHECK_ENABLED']:
            if not request.is_xhr:
                reason = (
                    'XHR checking failed - X-Requested-With not set '
                    'to XMLHttpRequest'
                )
                return self._error_response(reason)
            if not request.content_type == 'application/json':
                reason = (
                    'XHR checking failed - Content-Type not set '
                    'to application/json'
                )
                return self._error_response(reason)
        request.xhr_valid = True

    def exempt(self, view):
        """A decorator that can exclude a view from XHR checking.
        Remember to put the decorator above the `route`::
            xhr = XhrCheck(app)
            @xhr.exempt
            @app.route('/some-view', methods=['POST'])
            def some_view():
                return
        """
        view_location = '%s.%s' % (view.__module__, view.__name__)
        self._exempt_views.add(view_location)
        return view

    def _error_response(self, reason):
        return abort(403, reason)
