"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime

import simplejson as json

EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)


class UnixTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return (obj - EPOCH).total_seconds()
        return json.JSONEncoder.default(self, obj)
