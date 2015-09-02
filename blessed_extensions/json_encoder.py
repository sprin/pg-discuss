"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime
from flask import request
from simplejson import (
    JSONEncoder,
    JSONEncoderForHTML,
)

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt.replace(tzinfo = None) - epoch
    return delta.total_seconds()

class UnixTimeJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return unix_time(obj)
        return JSONEncoder.default(self, obj)

class IsoDateJSONEncoder(JSONEncoder):
    """Convert datetime objects to ISO 8601 strings. The exact format is
    "YYYY-MM-DDTHH:MM:SS.mmmmmmZ", which can be parsed directly by the
    JavaScript Date constructor.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat() + 'Z'
        return JSONEncoder.default(self, obj)

class UnixTimeJSONEncoderForHTML(JSONEncoderForHTML):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return unix_time(obj)
        return JSONEncoderForHTML.default(self, obj)

class IsoDateJSONEncoderForHTML(JSONEncoderForHTML):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat() + 'Z'
        return JSONEncoderForHTML.default(self, obj)

class SmartJSONEncoderBase(object):
    """Base class for "smart" JSON encoders that escape HTML by default,
    but will send unescaped HTML if the HTTP header `X-HTML-Escape` is set to
    0.

    This ensures that web clients that cannot be trusted to properly escape
    JSON data before rendering in to the DOM are protected from XSS by default,
    yet clients are allowed to request JSON that is not HTML-escaped when
    escaping is undesirable.
    """
    def __init__(self, *args, **kwargs):
        if request.headers.get('X-HTML-Escape') == '0':
            self.wrapped_class = self.no_html_escape_class(*args, **kwargs)
        else:
            self.wrapped_class = self.html_escape_class(*args, **kwargs)

    def __getattr__(self,attr):
        orig_attr = self.wrapped_class.__getattribute__(attr)
        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                # prevent wrapped_class from becoming unwrapped
                if result == self.wrapped_class:
                    return self
                return result
            return hooked
        else:
            return orig_attr

class SmartUnixTimeJSONEncoder(SmartJSONEncoderBase):
    no_html_escape_class = UnixTimeJSONEncoder
    html_escape_class = UnixTimeJSONEncoderForHTML

class SmartIsoDateJSONEncoder(SmartJSONEncoderBase):
    no_html_escape_class = IsoDateJSONEncoder
    html_escape_class = IsoDateJSONEncoderForHTML
