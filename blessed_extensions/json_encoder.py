"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime
from flask import request
from simplejson import JSONEncoder
from pg_discuss import _compat

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

class SmartJSONEncoderBase(object):
    """Base class for "smart" JSON encoders that escape HTML (using HTML entity
    escaping) by default, but will send unescaped HTML if the HTTP header
    `X-HTML-Escape` is set to 0.


    This ensures that web clients that cannot be trusted to properly escape
    JSON data before rendering in to the DOM are protected from XSS by default,
    yet clients are allowed to request JSON that is not HTML-escaped when
    escaping is undesirable.
    """
    def __init__(self, *args, **kwargs):
        self.wrapped_class = self.encoder_class(*args, **kwargs)

    def encode(self, *args, **kwargs):
        rv = self.wrapped_class.encode(*args, **kwargs)
        if request.headers.get('X-HTML-Escape') == '0':
            return rv
        return _compat.escape(rv)

class SmartUnixTimeJSONEncoder(SmartJSONEncoderBase):
    encoder_class = UnixTimeJSONEncoder

class SmartIsoDateJSONEncoder(SmartJSONEncoderBase):
    encoder_class = IsoDateJSONEncoder
