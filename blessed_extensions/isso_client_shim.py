"""Extension to adapt JSON API to format used by Isso JavaScript client.

If extensions that add edit/delete views are enabled, they must be loaded before
this extension.
"""
import datetime
from flask import request
from pg_discuss.ext import (
    AppExtBase,
    OnCommentPreSerialize,
)

class IssoClientShim(AppExtBase, OnCommentPreSerialize):
    def init_app(self, app):
        self.app = app
        # Disable all pretty-printing. Flask will not disable it since
        # `X-Requested-With: XMLHttpRequest` is not sent.
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        app.route('/', methods=['GET'])(self.fetch_)
        app.route('/new', methods=['POST'])(self.new_)
        app.route('/id/<int:comment_id>', methods=['GET'])(
            app.view_functions['view'])

        # Create routes to edit and delete views, if they have been configured.
        if 'edit' in app.view_functions:
            app.route('/id/<int:comment_id>', methods=['PUT'])(
                app.view_functions['edit'])

        if 'delete' in app.view_functions:
            app.route('/id/<int:comment_id>', methods=['DELETE'])(
                app.view_functions['delete'])

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        client_comment['parent'] = raw_comment['parent_id']

    def new_(self):
        """Create a new comments.
        Use the `uri` paramters as the thread `client_id`. Note that
        the client should configure the `uri` parameter to be a unique client
        id, not a uri.
        """
        thread_client_id = request.args.get('uri')
        return self.app.view_functions['new'](thread_client_id)

    def fetch_(self):
        """Fetch the list of comments associated with the thread.
        Use the `uri` paramters as the thread `client_id`.
        """
        thread_client_id = request.args.get('uri')
        resp = self.app.view_functions['fetch'](thread_client_id)
        resp.headers['Date'] = datetime.datetime.now().isoformat() + 'Z'
        return resp
