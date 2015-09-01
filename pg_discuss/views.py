"""
Minimal comment CRUD views, compatible with Isso client:
https://github.com/posativ/isso/blob/master/isso/js/app/api.js

 - fetch: fetch the list of comments for a thread
 - new: create a new comment
 - view: fetch a single comment
 - edit: update an existing comment
 - delete: delete a comment

Important: XSS Prevention
By defualt, the JSON returned by these views is not HTML-escaped. Any data
rendered in to the DOM must be HTML-escaped on the client-side. If you cannot
trust web clients to properly escape JSON data before rendering to HTML, it is
recommended to set `DRIVER_JSON_ENCODER` to a subclass of simplejson's
`JSONEncoderForHTML`, such as one of those in blessed_extensions.json_encoder.

JSON is not HTML-escaped by default because it is not presumed that all
clients are web clients.

"""

from flask import (
    jsonify,
    request,
)

from . import queries
from . import forms
from . import serialize

def fetch(thread_client_id):
    comments_seq = queries.fetch_comments_by_thread_client_id(thread_client_id)
    comments_seq = [serialize.to_client_comment(c) for c in comments_seq]
    return jsonify({'comments': comments_seq})

def new(thread_client_id):
    # Extract whitelisted attributes from request JSON
    # Note that extensions have the opportunity to process/persist additional
    # attributes from the request JSON, since they have access to the
    # request and `new_comment` object
    json = request.get_json()
    allowed_keys = ['parent_id', 'text']
    new_comment = {k: json[k] for k in allowed_keys if json.has_key(k)}

    # Validate required, type, text length
    new_comment = forms.validate_new_comment(new_comment)

    # Create empty `custom_json`, for extensions to populate.
    new_comment['custom_json'] = {}

    # Try to fetch the existing thread record
    try:
        thread = queries.fetch_thread_by_client_id(thread_client_id)
    except queries.ThreadNotFoundError:
        # Create a new thread record if one does not exist.
        thread = queries.insert_thread({'client_id': thread_client_id})

    new_comment['thread_id'] = thread['id']

    # Insert the comment
    comment = queries.insert_comment(new_comment)
    comment = serialize.to_client_comment(comment)
    return jsonify(comment)

def view(comment_id):
    # Fetch the comment
    comment = queries.fetch_comment_by_id(comment_id)
    comment = serialize.to_client_comment(comment)
    return jsonify(comment)
