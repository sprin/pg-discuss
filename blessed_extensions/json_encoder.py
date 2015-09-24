"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime

import simplejson as json

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt.replace(tzinfo = None) - epoch
    return delta.total_seconds()

class UnixTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return unix_time(obj)
        return json.JSONEncoder.default(self, obj)

class IsoDateJSONEncoder(json.JSONEncoder):
    """Convert datetime objects to ISO 8601 strings. The exact format is
    "YYYY-MM-DDTHH:MM:SS.mmmmmmZ", which can be parsed directly by the
    JavaScript Date constructor.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat() + 'Z'
        return json.JSONEncoder.default(self, obj)
