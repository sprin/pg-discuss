import codecs
import datetime
import functools

from flask import request
import pytz
import simplejson as json
import werkzeug
import werkzeug.security

from pg_discuss import ext


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
        # We interpret the client options slightly differently than the
        # Isso backend. `limit` is treated as a limit to the number of
        # direct descendants that will be returned for each node,
        # and `nested_limit` is treated as a limit to the depth of replies
        # returned.
        after = None
        try:
            # Because of a regression in Python 3, we must jump through
            # some hoops to correctly convert a Decimal string representing
            # a fractional Unix timestamp to a Datetime object.
            # See: https://bugs.python.org/issue23607
            # Naively using floats will result in comparison errors.
            after_str = request.args.get('after')
            if after_str:
                try:
                    seconds_str, ms_str = after_str.split('.')
                except ValueError:
                    seconds_str = after_str
                    ms_str = None

                after = datetime.datetime.fromtimestamp(
                    int(seconds_str),
                    tz=pytz.utc)
                if ms_str:
                    td = datetime.timedelta(microseconds=int(ms_str))
                    after = after + td
        except TypeError:
            pass

        try:
            reply_limit = int(request.args.get('limit'))
        except TypeError:
            reply_limit = None

        try:
            reply_depth_limit = int(request.args.get('nested_limit'))
        except TypeError:
            reply_depth_limit = None

        try:
            parent_id = int(request.args.get('parent'))
        except TypeError:
            parent_id = None

        # Change key to comment collection from "comments" to "replies"
        comment_tree = build_comment_tree(
            comment_seq=comment_seq,
            parent_id=parent_id,
            after=after,
            reply_limit=reply_limit,
            count_limit=None,
            reply_depth_limit=reply_depth_limit,
        )
        client_thread.update(comment_tree)
        del client_thread['comments']
        # Isso threads have a null `id` attribute
        client_thread['id'] = None

        # Add the count of all comments as `total_replies_in_thread`
        client_thread['total_replies_in_thread'] = client_thread['reply_count']

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
            max_age=int(self.app.permanent_session_lifetime.total_seconds())
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

        # Return response. Response will be further processed by
        # `on_new_comment_response` to set cookies.
        return self.app.view_functions['new'](thread_client_id)

    def fetch_(self):
        """Fetch the list of comments associated with the thread.
        Use the `uri` paramters as the thread `client_id`.
        """
        # Use the `uri` parameter as the thread `client_id`.
        thread_client_id = request.args.get('uri')
        # Render the landing page if there is no `uri` parameter.
        if not thread_client_id:
            return self.app.view_functions['landing']()
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


def build_comment_tree(comment_seq,
                       parent_id=None,
                       index=0,
                       after=None,
                       reply_limit=None,
                       count_limit=None,
                       reply_depth_limit=None):
    """Build the nested tree of comments, counting the number of replies to
    each comments as we go. Our goal is to have the subtree of comments
    that belong to the parent, starting at the specified index, with up
    to `count_limit` replies, sorted by chronological order, and no
    replies at a depth greater than `reply_depth_limit`. All this processing is
    expensive, but is a fairly intuitive way of selecting a subtree to allow
    for both incrementally loading long, flat threads as well as digging deeper
    into highly nested comments.

    We assume that the sequence of
    comments has been sorted by `created` time, which enables us to construct
    the tree by iterating over the list sequentially.

    Pagination:
    `parent` is the parent comment we want to retrieve nested comments for.
    If `parent` is None, then we assume we are retrieving the top-level
    comments.
    `index` is the index relative to the chronologically ordered set of
    comments to a parent (or, the top-level comments).
    """
    # Construct the full tree, starting from the parent.
    # Once we have the full tree starting from the parent, we can
    # sort/annotate/prune it however we like.
    comment_tree = construct_full_tree(comment_seq, parent_id)

    # Find index of the first comment created after `after`
    if after:
        for i, comment in enumerate(comment_tree['replies']):
            if comment['created'] > after:
                index = max(i, 0)
                break

    # We start by discarding all comments up to `index`.
    del comment_tree['replies'][:index]
    # We can now descend the tree and annotate each node with counts
    # of its descendants and later siblings+sibling descendants.
    annotate_counts(comment_tree)

    # We need to discard any nodes at a depth greater than `reply_depth_limit`.
    discard_beyond_depth_limit(comment_tree, depth_limit=reply_depth_limit)

    # Keep only the first `reply_limit` nodes for each subtree.
    # This ensures that there are not more than `reply_limit` replies
    # returned for any given comment.
    if reply_limit:
        keep_reply_limit(comment_tree, reply_limit)

    # Keep only the first `count_limit` nodes by chronology.
    # This puts an absolute limit on the number of comments returned.
    if count_limit:
        keep_count_limit(comment_tree, count_limit)

    return comment_tree


def construct_full_tree(comment_seq, parent_id=None):
    """Construct the full tree, given an ordered sequence of comments."""
    comment_tree = {'replies': []}
    comment_dict = {}

    for c in comment_seq:
        # Track which comment is the desired parent, if supplied.
        if parent_id and c['id'] == parent_id:
            parent = c

        c['replies'] = []
        # Index the comment into the dictionary by id.
        comment_dict[c['id']] = c
        # Increment the total comment count.

        # If no parent_id, must be a top-level comment.
        if not c['parent_id']:
            comment_tree['replies'].append(c)

        # Otherwise, this is a nested comment, and we append it to the replies
        # of the parent, using the map to look up the parent. The parent is
        # guaranteed to exist in the map, since our `comment_seq` array is
        # sorted by `created` time.
        else:
            comment_dict[c['parent_id']]['replies'].append(c)

    # Return the tree starting with the desired parent, if supplied.
    if parent_id:
        return parent
    # Else, return the complete tree.
    return comment_tree


def annotate_counts(node):
    """Recursive function to annotate each node with the count of all
    of it's descendants, as well as the count of all sibling comments plus
    their children, made after each node.
    """
    # If no replies, this is a leaf node. Stop and return 1.
    node['reply_count'] = 0
    if not node['replies']:
        return 1
    else:
        # Annotate descendants and sum counts.
        for r in node['replies']:
            node['reply_count'] += annotate_counts(r)
        # Once descendants are annotated with descendant counts,
        # annotate with the count of siblings and their children coming after
        # this node.
        after_count = 0
        for r in reversed(node['replies']):
            r['after_count'] = after_count
            after_count += r['reply_count'] + 1
        return node['reply_count'] + 1


def keep_reply_limit(node, reply_limit):
    """Keep only the first `count_limit` nodes by chronology."""
    def walk_tree_and_discard(n):
        # Discard any direct descendants beyond the `reply_limit`.
        if 'replies' in n:
            if len(n['replies']) > reply_limit:
                hidden_replies = n.get('hidden_replies', 0)
                c = n['replies'][reply_limit]
                num_discarded = c['after_count'] + c['reply_count'] + 1
                n['hidden_replies'] = hidden_replies + num_discarded

                del n['replies'][reply_limit:]

            # Recursively check the remaining replies.
            for r in n['replies']:
                walk_tree_and_discard(r)
    walk_tree_and_discard(node)


def keep_count_limit(node, count_limit):
    """Keep only the first `count_limit` nodes by chronology."""
    # First, we need to find the `created` time of the `count_limit`-th node.
    created_times = []

    def walk_tree_for_created(n):
        created = n.get('created')
        if created:
            created_times.append(n['created'])
        if 'replies' in n:
            for r in n['replies']:
                walk_tree_for_created(r)

    walk_tree_for_created(node)

    created_times.sort()

    keep_time = created_times[count_limit]

    def walk_tree_and_discard(n):
        # Discard any direct descendants that are greater than the time.
        if 'replies' in n:
            len_replies = len(n['replies'])
            num_discarded = 0
            for i in range(len_replies - 1, -1, -1):
                c = n['replies'][i]
                if c['created'] > keep_time:
                    num_discarded += c['after_count'] + c['reply_count'] + 1
                    del n['replies'][i]

            hidden_replies = n.get('hidden_replies', 0)
            n['hidden_replies'] = hidden_replies + num_discarded

        # Recursively check the remaining replies.
        for r in n['replies']:
            walk_tree_and_discard(r)
    walk_tree_and_discard(node)


def discard_beyond_depth_limit(node, depth_limit, cur_depth=0):
    """Discard nodes beyond the depth limit. The root is considered "level 0",
    and the first descendants are "level 1".
    """
    if cur_depth > depth_limit:
        del node['replies']
        node['deeper_replies'] = node['reply_count']
    else:
        for r in node['replies']:
            discard_beyond_depth_limit(r, depth_limit, cur_depth + 1)


def hash(val):
    salt = b"Eech7co8Ohloopo9Ol6baimi"
    hashed = werkzeug.security.pbkdf2_bin(
        val.encode('utf-8'), salt, 1000, 6, "sha1")
    return codecs.encode(hashed, "hex_codec").decode("utf-8")
