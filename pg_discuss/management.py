from flask import (
    current_app,
    url_for,
)
from flask.ext.script import Command

from ._compat import unquote

class ListRoutes(Command):
    """List all routes configured on application.
    """

    def run(self):
        """List all routes configured on application.
        """
        output = []
        for rule in current_app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = unquote("{:50s} {:20s} {}".format(
                rule.endpoint,
                methods,
                rule,
            ))
            output.append(line)

        for line in sorted(output):
            print(line)
