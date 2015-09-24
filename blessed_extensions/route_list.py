import flask
import flask_script

from pg_discuss import _compat
from pg_discuss import ext

class ListRoutes(flask_script.Command):
    """List all routes configured on application.
    """

    def run(self):
        """List all routes configured on application.
        """
        output = []
        for rule in flask.current_app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = _compat.unquote("{:50s} {:20s} {}".format(
                rule.endpoint,
                methods,
                rule,
            ))
            output.append(line)

        for line in sorted(output):
            print(line)

class RouteListExt(ext.AppExtBase):
    """Middleware to verify the request has Content-Type set to
    application/json for data-modifying views.
    This assumes that all, or most, data-modifying views are intended to handle
    JSON XHR requests.

    Register it with::
        app = Flask(__name__)
        CheckJsonMimetype(app)
    """

    def init_app(self, app):
        app.manager.add_command('list_routes', ListRoutes())
