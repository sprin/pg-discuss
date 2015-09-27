"""Module containing default and "blessed" JSON encoders/decoders.
"""
import datetime

import simplejson as json


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt.replace(tzinfo=None) - epoch
    return delta.total_seconds()


class UnixTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return unix_time(obj)
        return json.JSONEncoder.default(self, obj)
