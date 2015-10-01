import flask
from voluptuous import Schema

from pg_discuss import _compat
from pg_discuss import ext

#: Allow the author field to be changed by editing a comment.
CAPTURE_AUTHOR_ALLOW_EDIT = False


class CaptureAuthor(ext.AppExtBase, ext.ValidateComment,
                    ext.OnPreCommentSerialize):
    """Extension to capture and persist the author field from the HTTP API.

    Enables a setting, `CAPTURE_AUTHOR_ALLOW_EDIT`, which when True,
    allows the author field to be edited by the Identity which posted.
    """

    def init_app(self, app):
        self._app = app
        app.config.setdefault('CAPTURE_AUTHOR_ALLOW_EDIT',
                              CAPTURE_AUTHOR_ALLOW_EDIT)

    def validate_comment(self, comment, action, **extras):
        allow_edit = self._app.config['CAPTURE_AUTHOR_ALLOW_EDIT']
        if action == 'create' or allow_edit:
            author = flask.request.get_json().get('author')
            if author:
                comment['custom_json']['author'] = (
                    Schema(_compat.text_type)(author)
                )
        return comment

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        if 'author' in raw_comment['custom_json']:
            client_comment['author'] = raw_comment['custom_json']['author']
