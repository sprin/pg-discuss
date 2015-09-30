import voluptuous

from pg_discuss import ext

#: Minimum allowed comment length
MIN_COMMENT_LENGTH = 3
#: Maximum allowed comment length
MAX_COMMENT_LENGTH = 65535


class ValidateCommentLen(ext.ValidateComment):
    """Extension to add a validation rule that enforces a minimum and
    maximum comment length.
    """

    def __init__(self, app):
        app.config.setdefault('MIN_COMMENT_LENGTH', MIN_COMMENT_LENGTH)
        app.config.setdefault('MAX_COMMENT_LENGTH', MAX_COMMENT_LENGTH)
        super(ext.ValidateComment, self).__init__(app)

    def validate_comment(self, comment, action, **extras):
        text = comment['text']
        min_comment_length = self.app.config['MIN_COMMENT_LENGTH']
        max_comment_length = self.app.config['MAX_COMMENT_LENGTH']
        voluptuous.Length(min=min_comment_length, max=max_comment_length)(
            text.rstrip())
        return comment
