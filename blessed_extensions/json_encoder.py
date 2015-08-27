"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime
from flask.json import JSONEncoder

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

class UnixTimeJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return unix_time(obj)
        return JSONEncoder.default(self, obj)

class IsoDateJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)
