"""Extension to add a validation rule that enforces a minimum and
maximum comment length.
"""
import voluptuous

from pg_discuss import ext


class ValidateCommentLen(ext.ValidateComment):

    def __init__(self, app):
        app.config.setdefault('MIN_COMMENT_LENGTH', 3)
        app.config.setdefault('MAX_COMMENT_LENGTH', 65535)
        super(ext.ValidateComment, self).__init__(app)

    def validate_comment(self, comment, action, **extras):
        text = comment['text']
        min_comment_length = self.app.config['MIN_COMMENT_LENGTH']
        max_comment_length = self.app.config['MAX_COMMENT_LENGTH']
        voluptuous.Length(min=min_comment_length, max=max_comment_length)(
            text.rstrip())
        return comment
