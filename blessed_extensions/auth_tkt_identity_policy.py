from flask import session
from pg_discuss import queries
from pg_discuss import ext

class AuthTktIdentityPolicy(ext.IdentityPolicy):

    def remember(self, request, identity_id, **extras):
        # Update cookie
        session['identity_id'] = identity_id

    def get_identity(self, request, **extras):
        identity_id = session.get('identity_id')
        from flask import current_app
        if identity_id:
            try:
                return queries.fetch_identity(identity_id)
            # If we have a cookie, but no matching identity in the db,
            # create a new identity and reset cookie.
            except queries.IdentityNotFoundError:
                return queries.insert_identity()
        else:
            current_app.logger.error(identity_id)
            return queries.insert_identity()

    def forget(self, request, **extras):
        session.pop('identity_id')
