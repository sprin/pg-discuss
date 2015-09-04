from flask import (
    abort,
    request,
)

from pg_discuss import ext

class JsonMimetypeExt(ext.AppExtBase):
    """Middleware to verify the request has Content-Type set to
    application/json for data-modifying views.
    This assumes that all, or most, data-modifying views are intended to handle
    JSON XHR requests.

    Register it with::
        app = Flask(__name__)
        CheckJsonMimetype(app)
    """

    def init_app(self, app):
        self._app = app
        self._exempt_views = []

        app.config.setdefault('JSON_MIMETYPE_CHECK_DEFAULT', True)
        app.config.setdefault('JSON_MIMETYPE_EXEMPT_METHODS',
                              ['GET', 'HEAD', 'OPTIONS', 'TRACE'])

        if not app.config['JSON_MIMETYPE_CHECK_DEFAULT']:
            return

        @app.before_request
        def _check_mimetype():
            if request.method in app.config['JSON_MIMETYPE_EXEMPT_METHODS']:
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
            self.check_mimetype()

    def check_mimetype(self):
        if request.mimetype != 'application/json':
            reason = (
                'Mimetype checking failed - Content-Type not set '
                'to application/json'
            )
            return self._error_response(reason)
        request.json_mimetype_valid = True

    def exempt(self, view):
        """A decorator that can exclude a view from JSON mimetype checking.
        Remember to put the decorator above the `route`::
            json_mimetype = CheckJsonMimetype(app)
            @json_mimetype.exempt
            @app.route('/some-view', methods=['POST'])
            def some_view():
                return
        """
        view_location = '%s.%s' % (view.__module__, view.__name__)
        self._exempt_views.append(view_location)
        return view

    def _error_response(self, reason):
        return abort(400, reason)
