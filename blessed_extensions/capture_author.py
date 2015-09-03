from flask import request
from voluptuous import (
    Schema,
)

from pg_discuss import ext

class CaptureAuthor(ext.ValidateComment, ext.OnCommentPreSerialize):
    def validate_comment(self, comment, **extras):
        author = request.get_json().get('author')
        if author:
            comment['custom_json']['author'] = Schema(unicode)(author)
        return comment

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        if 'author' in raw_comment['custom_json']:
            client_comment['author'] = raw_comment['custom_json']['author']
