import re

import flask
from voluptuous import (
    All,
    Invalid,
    Schema,
)

from pg_discuss import _compat
from pg_discuss import ext


class CaptureEmail(ext.ValidateComment):
    """Extension to capture and persist the email field from the HTTP API.
    """
    def validate_comment(self, comment, action, **extras):
        email = flask.request.get_json().get('email')
        if email:
            form = Schema(All(_compat.text_type, validate_email))
            comment['custom_json']['email'] = form(email)
        return comment


def validate_email(v):
    if re.match("[\w\.\-\+]*@[\w\.\-]*\.\w+", v):
        return v
    else:
        raise Invalid("email is not in recognized format: {0}".format(v))
