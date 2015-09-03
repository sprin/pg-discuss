from flask import request
from pg_discuss import ext

class CaptureRemoteAddr(ext.ValidateComment):
    def validate_comment(self, comment, **extras):
        comment['custom_json']['remote_addr'] = request.remote_addr
        return comment
