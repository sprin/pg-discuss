import re
from flask import request
from voluptuous import (
    All,
    Schema,
    Invalid,
)

from pg_discuss import ext
from pg_discuss import _compat

class CaptureEmail(ext.ValidateComment):
    def validate_comment(self, comment, action, **extras):
        email = request.get_json().get('email')
        if email:
            comment['custom_json']['email'] = Schema(
                All(_compat.text_type, validate_email))(email)
        return comment

def validate_email(v):
    if re.match("[\w\.\-\+]*@[\w\.\-]*\.\w+", v):
        return v
    else:
        raise Invalid("email is not in recognized format: {0}".format(v))
