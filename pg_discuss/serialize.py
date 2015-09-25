"""Functions to prepare comments and threads for serialization."""
import flask
import markupsafe

from . import ext
from . import _compat

# Fields which will be serialized by default when sent to client.
DEFAULT_COMMENT_WHITELIST = [
    'id',
    'thread_id',
    'parent_id',
    'created',
    'modified',
    'text',
]

DEFAULT_THREAD_WHITELIST = [
    'id',
    'client_id',
]


def to_client_comment(raw_comment, plain=False):
    """Prepare comments for serialization to JSON.

    Only preserves whitelisted attributes. Calls any `OnPreCommentSerialize`
    extensions, and the CommentRenderer driver.
    """
    client_comment = {k: raw_comment[k] for k in DEFAULT_COMMENT_WHITELIST}

    # Extract `deleted` attribute from custom json as well.
    if 'deleted' in raw_comment['custom_json']:
        client_comment['deleted'] = raw_comment['custom_json']['deleted']

    # Run on_comment_serialize hooks
    ext.exec_hooks(ext.OnPreCommentSerialize, raw_comment, client_comment)

    # Escape string fields, besides `text`, which may be rendered into DOM.
    for k, v in client_comment.items():
        if isinstance(v, _compat.string_types) and k != 'text':
            client_comment[k] = markupsafe.escape(v)

    # Render comment text using configured CommentRenderer. Th renderer should
    # handle escaping of the comment text.
    if not plain:
        client_comment['text'] = (
            flask.current_app.comment_renderer.render(client_comment['text'])
        )

    return client_comment


def to_client_thread(raw_thread, comment_seq):
    """Prepare thread and it's comment collection for serialization to JSON.

    Only preserves whitelisted attributes. Calls any `OnPreThreadSerialize`
    extensions.

    Return value is an object whose JSON representation is the response.
    """
    client_thread = {k: raw_thread[k] for k in DEFAULT_THREAD_WHITELIST}

    client_thread['comments'] = comment_seq

    # Run on_pre_thread_serialize hooks
    ext.exec_hooks(ext.OnPreThreadSerialize, raw_thread, comment_seq,
                   client_thread)

    return client_thread
