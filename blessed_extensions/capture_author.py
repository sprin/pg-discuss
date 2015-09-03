from flask import request
from voluptuous import (
    Schema,
)

from pg_discuss import ext

class CaptureAuthor(ext.AppExtBase, ext.ValidateComment, ext.OnCommentPreSerialize):

    def init_app(self, app):
        self._app = app
        app.config.setdefault('CAPTURE_AUTHOR_ALLOW_EDIT', False)

    def validate_comment(self, comment, action, **extras):
        allow_edit = self._app.config['CAPTURE_AUTHOR_ALLOW_EDIT']
        if action == 'new' or allow_edit:
            author = request.get_json().get('author')
            if author:
                comment['custom_json']['author'] = Schema(unicode)(author)
        return comment

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        if 'author' in raw_comment['custom_json']:
            client_comment['author'] = raw_comment['custom_json']['author']
