import datetime
from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.total_seconds()
        return JSONEncoder.default(self, obj)
