"""Core JSON encoder. Converts DateTime object to ISO 8601 date strings.

Note that subclassing `JSONEncoder` is not recommended by the author of
`simplejson` since it is possible to have conflicts with attributes on the
parent class, or depend on attributes on the parent class that may be changed.
Also, the author suggests subclassing will be faster since `JSONEncoder` can
perform "caching of instances when certain arguments are not overriden." The
author's recommendation to implement the strategy pattern for JSON encoders is
to implement the strategy as a "default" callable that is passed to
`JSONEncoder` as an argument.
See: https://github.com/simplejson/simplejson/issues/124

However, subclasses which provide a new `default` method without acessing or
modifying other `JSONEncoder` internals should not have these drawbacks.
Timing of this `JSONEncoder` subclass did not show any difference compared to
providing a "default" callable.

Finally, Flask offers some JSON helpers, and assumes the user
will set `app.json_encoder` to a `JSONEncoder` subclass if a custom encoder
is needed. Therefore, pg-discuss will likewise expect subclasses of
`JSONEncoder` for the value of `DRIVER_JSON_ENCODER`.
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
