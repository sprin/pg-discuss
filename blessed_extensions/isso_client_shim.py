import codecs
import collections
import datetime
import functools

from flask import request
import simplejson as json
import werkzeug
import werkzeug.security

from pg_discuss import ext


#: Maximum depth of replies to be returned from the fetch API.
MAX_REPLY_DEPTH = 10

class IssoClientShim(ext.AppExtBase, ext.OnPreCommentSerialize,
                     ext.OnPreThreadSerialize, ext.OnPreCommentInsert,
                     ext.OnNewCommentResponse):
    """Extension to adapt JSON API to format used by Isso JavaScript client.

    If extensions that add edit/delete views are enabled, they must be loaded
    before this extension.
    """

    def init_app(self, app):
        # Disable all pretty-printing. Flask will not disable it since
        # `X-Requested-With: XMLHttpRequest` is not sent.
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        app.config.setdefault('MAX_REPLY_DEPTH', MAX_REPLY_DEPTH)

        views = app.view_functions

        # Exempt public read-only views from IdentityPolicy
        app.identity_policy_mgr.exempt(self.fetch_)
        app.identity_policy_mgr.exempt(self.count)

        app.route('/', methods=['GET'])(self.fetch_)
        app.route('/new', methods=['POST'])(self.new_)
        app.route('/id/<int:comment_id>', methods=['GET'])(views['view'])
        app.route('/count', methods=['POST'])(self.count)
        app.route('/id/<int:comment_id>', methods=['PUT'])(views['edit'])
        app.route('/id/<int:comment_id>', methods=['DELETE'])(views['delete'])
        app.route('/id/<int:comment_id>/like', methods=['POST'])(self.like_)
        app.route('/id/<int:comment_id>/dislike', methods=['POST'])(
            self.dislike_)

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        # Change `parent_id` key to `parent`
        client_comment['parent'] = raw_comment.pop('parent_id')

        # Change `upvotes` to `likes`, `downvotes` to `dislikes`
        if 'upvotes' in client_comment:
            client_comment['likes'] = client_comment.pop('upvotes')
        if 'downvotes' in client_comment:
            client_comment['dislikes'] = client_comment.pop('downvotes')

        client_comment['hash'] = raw_comment['custom_json'].get('hash')

        # Set "mode" to 4 for deleted comments
        if raw_comment['custom_json'].get('deleted'):
            client_comment['mode'] = 4

    def on_pre_thread_serialize(self, raw_thread, comment_seq, client_thread,
                                **extras):
        try:
            top_limit = int(request.args.get('limit'))
        except TypeError:
            top_limit = None
        try:
            nested_limit = int(request.args.get('nested_limit'))
        except TypeError:
            nested_limit = None

        reply_depth_limit = self.app.config['MAX_REPLY_DEPTH']

        # Change key to comment collection from "comments" to "replies"
        client_thread['replies'] = build_comment_tree_iter(
            comment_seq,
            top_limit,
            nested_limit,
            reply_depth_limit,
        )
        del client_thread['comments']

        # Add the count of top-level comments under key `total_replies'
        client_thread['total_replies'] = len(client_thread['replies'])

    def on_pre_comment_insert(self, new_comment, **extras):
        """Hash email, or remote_addr.

        If neither available, just skip hashing.
        """
        custom_json = new_comment['custom_json']
        val_to_hash = (
            custom_json.get('email')
            or custom_json.get('remote_addr')
        )
        if val_to_hash:
            custom_json['hash'] = hash(val_to_hash)

    def on_new_comment_response(self, resp, raw_comment, client_comment,
                                **extras):
        """Set a cookie to allow the client to edit/delete the comment.
        """
        # Set a cookie with a non-empty string value.
        # It does not matter to the client what the value is, just so long
        # as it is non-empty. Identitys are authenticated through another
        # means.
        cookie = functools.partial(
            werkzeug.dump_cookie,
            value='.',
            max_age=self.app.permanent_session_lifetime.total_seconds()
        )

        comment_id = raw_comment['id']

        resp.headers.add("Set-Cookie", cookie(str(comment_id)))
        resp.headers.add("X-Set-Cookie", cookie("isso-%i" % comment_id))

        return resp

    def new_(self):
        """Create a new comments.
        Use the `uri` paramters as the thread `client_id`. Note that
        the client should configure the `uri` parameter to be a unique client
        id, not a uri.
        """
        # Use the `uri` parameter as the thread `client_id`.
        thread_client_id = request.args.get('uri')

        # Set `parent_id` to parent.
        json_data = request.get_json()
        json_data['parent_id'] = json_data.get('parent')
        print(json_data['parent_id'])

        # Return response. Response will be further processed by
        # `on_new_comment_response` to set cookies.
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

    def like_(self, comment_id):
        resp = self.app.view_functions['upvote'](comment_id)
        return rename_voting_keys(resp)

    def dislike_(self, comment_id):
        resp = self.app.view_functions['downvote'](comment_id)
        return rename_voting_keys(resp)


def rename_voting_keys(resp):
    d = json.loads(resp.get_data())
    d['likes'] = d.pop('upvotes')
    d['dislikes'] = d.pop('downvotes')
    resp.set_data(json.dumps(d))
    return resp


def build_comment_tree_iter(comment_seq, top_limit=None, nested_limit=None,
                            reply_depth_limit=None):
    """Build the nested tree of comments, counting the number of replies to
    each comments as we go. Iterative version.
    """
    result = []
    current_level = {}
    parent_id_map = collections.defaultdict(list)
    top_level_count = 0
    nested_count = 0
    # Build a map of the top-level comments as `current_level` and
    # and build a map of parent ids to their replies.
    for c in comment_seq:
        c['replies'] = []
        c['total_replies'] = 0
        if not c['parent_id'] and top_level_count < top_limit:
            result.append(c)
            current_level[c['id']] = c
            top_level_count += 1
        else:
            parent_id = c['parent_id']
            parent_id_map[parent_id].append(c)

    # Build the comment tree by non-recursively collecting all the replies for
    # the current level, then collecting all replies for the next level, etc.
    # Ignore any replies that are beyond `nested_limit`.
    depth = 0
    while parent_id_map:
        parents = list(current_level.values())
        depth += 1
        if reply_depth_limit and depth >= reply_depth_limit:
            break
        for parent in parents:
            replies = parent_id_map.pop(parent['id'], None)
            if replies:
                nested_count += len(replies)
                if nested_count >= nested_limit:
                    break
                else:
                    parent['total_replies'] = nested_count
                    parent['replies'] = replies
                # Add replies to next round of iteration
                for r in replies:
                    current_level[r['id']] = r
            del current_level[parent['id']]

    return result


def hash(val):
    salt = b"Eech7co8Ohloopo9Ol6baimi"
    hashed = werkzeug.security.pbkdf2_bin(
        val.encode('utf-8'), salt, 1000, 6, "sha1")
    return codecs.encode(hashed, "hex_codec").decode("utf-8")
