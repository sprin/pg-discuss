from . import ext

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

def to_client_comment(raw_comment):
    """Prepare comments for serialization to JSON.

    Only preserves whitelisted attributes. Calls any `OnCommentPreSerialize`
    extensions.
    """
    client_comment = {k: raw_comment[k] for k in DEFAULT_COMMENT_WHITELIST}

    # Run on_comment_serialize hooks
    ext.exec_hooks(ext.OnCommentPreSerialize, raw_comment, client_comment)

    return client_comment

def to_client_thread(raw_thread):
    """Prepare threads for serialization to JSON.

    Only preserves whitelisted attributes. Calls any `OnThreadPreSerialize`
    extensions.
    """
    client_thread = {k: raw_thread[k] for k in DEFAULT_THREAD_WHITELIST}

    # Run on_comment_serialize hooks
    ext.exec_hooks(ext.OnPreThreadSerialize, raw_thread, client_thread)

    return client_thread
