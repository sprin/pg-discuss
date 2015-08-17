"""
Minimal comment CRUD views, compatible with Isso client:
https://github.com/posativ/isso/blob/master/isso/js/app/api.js

 - fetch: fetch the list of comments for a thread
 - new: create a new comment
 - view: fetch a single comment
 - edit: update an existing comment
 - delete: delete a comment
"""

from functools import wraps
from flask import (
    abort,
    request,
)

from pg_discuss.csrf import generate_csrf

def xhr(f):
    """Decorator to verify Content-Type header is set to 'application/json'.

    Note that this does not necessarily protect against CSRF if browsers
    implement "HTML JSON form submission":
    http://www.w3.org/TR/html-json-forms/

    The CsrfProtect middleware (enabled by default) must be enabled for full
    token-based CSRF protection.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.content_type == 'application/json':
            raise abort(403)
        return f(*args, **kwargs)
    return decorated_function

def fetch():
    pass

@xhr
def new():
    pass

def view():
    pass

@xhr
def edit():
    pass

@xhr
def delete():
    pass

def csrftoken():
    return generate_csrf()
