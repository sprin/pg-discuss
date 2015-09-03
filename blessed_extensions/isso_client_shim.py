"""Extension to adapt JSON API to format used by Isso JavaScript client.

If extensions that add edit/delete views are enabled, they must be loaded before
this extension.
"""
import datetime
from flask import request
from pg_discuss.ext import (
    AppExtBase,
    OnCommentPreSerialize,
    OnCommentCollectionPreSerialize,
)

class IssoClientShim(AppExtBase, OnCommentPreSerialize,
                     OnCommentCollectionPreSerialize):
    def init_app(self, app):
        self.app = app
        # Disable all pretty-printing. Flask will not disable it since
        # `X-Requested-With: XMLHttpRequest` is not sent.
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        app.route('/', methods=['GET'])(self.fetch_)
        app.route('/new', methods=['POST'])(self.new_)
        app.route('/id/<int:comment_id>', methods=['GET'])(
            app.view_functions['view'])
        app.route('/count', methods=['POST'])(self.count)

        # Create routes to edit and delete views, if they have been configured.
        if 'edit' in app.view_functions:
            app.route('/id/<int:comment_id>', methods=['PUT'])(
                app.view_functions['edit'])

        if 'delete' in app.view_functions:
            app.route('/id/<int:comment_id>', methods=['DELETE'])(
                app.view_functions['delete'])

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        client_comment['parent'] = raw_comment['parent_id']

    def on_comment_collection_preserialize(self, comment_seq, collection_obj,
                                           **extras):
        # Change key to comment collection from "comments" to "replies"
        collection_obj['replies'] = build_comment_tree(comment_seq)
        del collection_obj['comments']

        # Add the count of top-level comments under key `total_replies'
        collection_obj['total_replies'] = len(collection_obj['replies'])

    def new_(self):
        """Create a new comments.
        Use the `uri` paramters as the thread `client_id`. Note that
        the client should configure the `uri` parameter to be a unique client
        id, not a uri.
        """
        # Use the `uri` parameter as the thread `client_id`.
        thread_client_id = request.args.get('uri')

        # Set `parent_id` to parent.
        json = request.get_json()
        json['parent_id'] = json['parent']

        return self.app.view_functions['new'](thread_client_id)

    def fetch_(self):
        """Fetch the list of comments associated with the thread.
        Use the `uri` paramters as the thread `client_id`.
        """
        # Use the `uri` parameter as the thread `client_id`.
        thread_client_id = request.args.get('uri')
        resp = self.app.view_functions['fetch'](thread_client_id)
        # Set a `Date` HTTP header with the current datetime.
        resp.headers['Date'] = datetime.datetime.now().isoformat() + 'Z'
        return resp

    def count(self):
        """Not implemented, stubbed to satisfy client.
        """
        return '[]'

def build_comment_tree(comment_seq, parent_id=None):
    """Build the nested tree of comments, counting the number of replies to
    each comment along the way.
    """
    children = [c for c in comment_seq if c['parent_id'] == parent_id]
    for c in children:
        c['replies'] = build_comment_tree(comment_seq, c['id'])
        c['total_replies'] = len(c['replies'])
    return children
