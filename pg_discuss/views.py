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

from pg_discuss.csrf import generate_csrf
from pg_discuss import queries
from pg_discuss import forms

def fetch():
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

    # Insert the comment
    result = queries.insert_comment(new_comment)
    return jsonify(result)

def view():
    pass

def edit():
    pass

def delete():
    pass

def csrftoken():
    return generate_csrf()
