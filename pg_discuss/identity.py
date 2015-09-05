from flask import (
    request,
    g,
)

class IdentityPolicyManager(object):
    """Middleware to execute the configured IdentityPolicy.
    """

    def __init__(self, app, identity_policy_cls):
        self.identity_policy = identity_policy_cls()
        self._exempt_views = []

        app.config.setdefault('IDENTITY_POLICY_EXEMPT_METHODS', ['OPTIONS'])

        @app.before_request
        def _auth_before_request():
            if request.method in app.config['IDENTITY_POLICY_EXEMPT_METHODS']:
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
            return self.auth_before_request()

    def auth_before_request(self):
        # Get the identity object.
        identity = self.identity_policy.get_identity(request)

        if identity:
            # Store the identity object on the `g` request global.
            g.identity = identity

            # Remember the identity.
            self.identity_policy.remember(request, identity['id'])

    def exempt(self, view):
        """A decorator that can exclude a view from JSON mimetype checking.
        Remember to put the decorator above the `route`::
            identity_policy_mgr = IdentityPolicyManager(app)
            @identity_policy_mgr.exempt
            @app.route('/some-view', methods=['GET'])
            def some_view():
                return
        """
        view_location = '%s.%s' % (view.__module__, view.__name__)
        self._exempt_views.append(view_location)
        return view