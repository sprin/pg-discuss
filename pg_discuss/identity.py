"""Middleware to execute the configured `IdentityPolicy`.
"""
import flask

class IdentityPolicyManager(object):
    """Middleware to execute the configured IdentityPolicy.

    Before each request, calls the `get_identity` method of the
    configured `IdentityPolicy`. The `IdentityPolicy` may return an identity
    object, which is then assigned to the `flask.g` request global and the
    `remember` method of the `IdentityPolicy` method is invoked with the
    identity. If no identity is returned by the `IdentityPolicy`, request
    processing continues normally without the identity.
    """

    def __init__(self, app, identity_policy_cls):
        self.identity_policy = identity_policy_cls(app)
        self._exempt_views = []

        app.config.setdefault('IDENTITY_POLICY_EXEMPT_METHODS', ['OPTIONS'])

        @app.before_request
        def _auth_before_request():
            """Check if the request is exempted from the `IdentityPolicy`
            before invoking it.
            """
            if (
                flask.request.method in
                app.config['IDENTITY_POLICY_EXEMPT_METHODS']
            ):
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
            return self.auth_before_request()

    def auth_before_request(self):
        """Get the identity object from the `IdentityPolicy`. If an identity is
        returned, set it on the `flask.g` request global and remember it.
        """
        identity = self.identity_policy.get_identity(flask.request)

        if identity:
            # Store the identity object on the `g` request global.
            flask.g.identity = identity

            # Remember the identity.
            self.identity_policy.remember(flask.request, identity['id'])

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
