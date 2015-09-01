from flask import (
    jsonify,
)

from pg_discuss.ext import (
    AppExtBase,
    OnCommentPreSerialize,
)
from pg_discuss import queries

class DeleteViewExt(AppExtBase, OnCommentPreSerialize):
    def init_app(self, app):
        app.route('/comments/<int:comment_id>', methods=['DELETE'])(delete)

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        if 'deleted' in raw_comment['custom_json']:
            client_comment['deleted'] = raw_comment['custom_json']['deleted']

def delete(comment_id):
    """Mark a comment as deleted. The comment will still show up in API reults,
    but only containing values for it's `id`, `tid`, `parent`.

    Note that the actual database record is not deleted. Deletes are handled
    in the same way that edits are: the record is updated in place, and an
    archive is made of the old record. The `deleted` flag may be used to
    indicate special rendering of deleted comments.
    """
    comment_edit = {
        'text': '',
        'custom_json_patch': {
            'deleted': True,
        }
    }

    # Mark the comment as deleted
    result = queries.update_comment(
        comment_id,
        comment_edit,
        update_modified=True
    )
    return jsonify(result)
