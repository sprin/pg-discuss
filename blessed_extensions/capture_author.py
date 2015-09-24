import flask
from voluptuous import Schema

from pg_discuss import _compat
from pg_discuss import ext

class CaptureAuthor(ext.AppExtBase, ext.ValidateComment,
                    ext.OnPreCommentSerialize):

    def init_app(self, app):
        self._app = app
        app.config.setdefault('CAPTURE_AUTHOR_ALLOW_EDIT', False)

    def validate_comment(self, comment, action, **extras):
        allow_edit = self._app.config['CAPTURE_AUTHOR_ALLOW_EDIT']
        if action == 'new' or allow_edit:
            author = flask.request.get_json().get('author')
            if author:
                comment['custom_json']['author'] = (
                    Schema(_compat.text_type)(author)
                )
        return comment

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        if 'author' in raw_comment['custom_json']:
            client_comment['author'] = raw_comment['custom_json']['author']
