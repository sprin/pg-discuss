import flask

from pg_discuss import ext


class CaptureRemoteAddr(ext.ValidateComment):
    """Extension to capture and persist the IP address associated with comment
    submissions.
    """
    def validate_comment(self, comment, action, **extras):
        comment['custom_json']['remote_addr'] = flask.request.remote_addr
        return comment
