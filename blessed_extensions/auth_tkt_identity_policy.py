import flask

from pg_discuss import ext
from pg_discuss import queries

class AuthTktIdentityPolicy(ext.IdentityPolicy):
    """An IdentityPolicy tied to a browser session via a cookie.

    This policy does not provide for any authentication, but simply
    associates an identity with a browser session so that a user may
    edit/delete comments associated with their browser session.

    This policy does not attempt to enforce that users supply a consistent
    name/email for each comment. It does persist names and emails with
    the Identity record for the sake of labeling identities, but otherwise,
    names/emails have no functional importance with this policy.
    """

    def __init__(self, app):
        self.app = app
        # Enable the related extension to persist comment info
        # with the session identity.
        app.config.setdefault('ENABLE_EXT_BLESSED_PERSIST_COMMENT_INFO_ON_ID', True)

    def remember(self, request, identity_id, **extras):
        # Update cookie
        flask.session['identity_id'] = identity_id

    def get_identity(self, request, **extras):
        identity_id = flask.session.get('identity_id')
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
        flask.session.pop('identity_id')

class PersistCommentInfoOnIdentity(ext.OnPostCommentInsert):

    def on_post_comment_insert(self, comment):
        """Update Identity record with name and email entered for comment.
        Since there is not necessarily an enforcement that names and emails are
        required or consistent across comments from the same identity, we treat
        names and emails as a set.

        If name/email are not captured, then this is a NOP.
        """
        new_name = comment['custom_json'].get('author')
        known_names = flask.g.identity['custom_json'].get('names', [])
        identity_edit = {'custom_json': {}}
        if new_name and new_name not in known_names:
            known_names.append(new_name)
            identity_edit['custom_json']['names'] = known_names

        new_remote_addr = comment['custom_json'].get('remote_addr')
        known_remote_addrs = flask.g.identity['custom_json'].get(
            'remote_addrs', [])
        if new_remote_addr and new_remote_addr not in known_remote_addrs:
            known_remote_addrs.append(new_remote_addr)
            identity_edit['custom_json']['remote_addrs'] = known_remote_addrs

        new_email = comment['custom_json'].get('email')
        known_emails = flask.g.identity['custom_json'].get('emails', [])
        if new_email and new_email not in known_emails:
            known_emails.append(new_email)
            identity_edit['custom_json']['emails'] = known_emails

        if identity_edit['custom_json']:
            flask.g.identity = queries.update_identity(
                flask.g.identity['id'],
                identity_edit,
                flask.g.identity,
            )
