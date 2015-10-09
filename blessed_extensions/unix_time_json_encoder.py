"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime

import pytz
import simplejson as json

EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)


class UnixTimeJSONEncoder(json.JSONEncoder):
    """JSON encoder driver to encode datetime values as Unix timestamps.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return (obj - EPOCH).total_seconds()
        return json.JSONEncoder.default(self, obj)
