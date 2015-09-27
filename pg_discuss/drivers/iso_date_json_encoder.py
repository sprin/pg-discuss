"""Core JSON encoder. Converts DateTime object to ISO 8601 date strings.
"""
import datetime

import simplejson as json


class IsoDateJSONEncoder(json.JSONEncoder):
    """Convert datetime objects to ISO 8601 strings. The exact format is
    "YYYY-MM-DDTHH:MM:SS.mmmmmmZ", which can be parsed directly by the
    JavaScript Date constructor.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat() + 'Z'
        return json.JSONEncoder.default(self, obj)
