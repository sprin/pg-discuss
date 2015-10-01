import flask
import flask_script

from pg_discuss import _compat
from pg_discuss import ext


class RouteListExt(ext.AppExtBase):
    """Extension to add a command to list the currently configured routes
    in the application.

    Useful since extensions can add routes at runtime.
    """

    def init_app(self, app):
        app.script_manager.add_command('list_routes', ListRoutes())


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
