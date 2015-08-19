"""
Minimal comment CRUD views, compatible with Isso client:
https://github.com/posativ/isso/blob/master/isso/js/app/api.js

 - fetch: fetch the list of comments for a thread
 - new: create a new comment
 - view: fetch a single comment
 - edit: update an existing comment
 - delete: delete a comment
"""

from flask import (
    jsonify,
    request,
)

from .csrf import generate_csrf
from . import queries
from . import forms

def fetch(name):
    pass

def new():
    # Extract whitelisted attributes from request JSON
    # Note that extensions have the opportunity to process/persist additional
    # attributes from the request JSON, since they have access to the
    # request and `new_comment` object
    json = request.get_json()
    allowed_keys = ['parent', 'text']
    new_comment = {k: json[k] for k in allowed_keys if json.has_key(k)}

    # Validate required, type, text length
    new_comment = forms.validate_new_comment(new_comment)

    # TODO: Using dummy tid. Replace with real tid.
    new_comment['tid'] = 1

    # Insert the comment
    result = queries.insert_comment(new_comment)
    return jsonify(result)

def view(comment_id):
    # Fetch the comment
    result = queries.fetch_comment(comment_id)
    return jsonify(result)

def edit(comment_id):
    json = request.get_json()
    allowed_keys = ['text']
    comment_edit = {k: json[k] for k in allowed_keys if json.has_key(k)}

    # Validate required, type, text length
    # Use the id given in the URL path, ignoring any in the request JSON
    comment_edit = forms.validate_comment_edit(comment_edit)

    # Update the comment
    result = queries.update_comment(comment_id, comment_edit)
    return jsonify(result)

def delete(comment_id):
    """Mark a comment as deleted. The comment will still show up in API reults,
    but only containing values for it's `id`, `tid`, `parent`.

    Note that the actual database record is not deleted. Deletes are handled
    in the same way that edits are: the record is updated in place, and an
    archive is made of the old record. The `deleted` flag may be used to
    indicate special rendering of deleted comments.
    """
    comment_edit = {
        'deleted': True,
        'text': '',
    }

    # Mark the comment as deleted
    result = queries.update_comment(comment_id, comment_edit)
    return jsonify(result)

def csrftoken():
    return generate_csrf()
