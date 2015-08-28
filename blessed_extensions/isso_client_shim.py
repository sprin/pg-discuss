"""Extension to adapt JSON API to format used by Isso JavaScript client.

If extensions that add edit/delete views are enabled, they must be loaded before
this extension.
"""
from pg_discuss.ext import AppExtBase

class IssoClientShim(AppExtBase):
    def init_app(self, app):
        app.route('/', methods=['GET'])(app.view_functions['fetch'])
        app.route('/new', methods=['POST'])(app.view_functions['new'])
        app.route('/id/<int:comment_id>', methods=['GET'])(
            app.view_functions['view'])

        # Create routes to edit and delete views, if they have been configured.
        if 'edit' in app.view_functions:
            app.route('/id/<int:comment_id>', methods=['PUT'])(
                app.view_functions['edit'])

        if 'delete' in app.view_functions:
            app.route('/id/<int:comment_id>', methods=['DELETE'])(
                app.view_functions['delete'])
