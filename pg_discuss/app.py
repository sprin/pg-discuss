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
    Flask,
    abort,
    request,
)

from pg_discuss.csrf import CsrfProtect, generate_csrf

app = Flask('pg-discuss')
CsrfProtect(app)


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

@app.route('/', methods=['GET'])
def fetch():
    pass

@xhr
@app.route('/new', methods=['POST'])
def new():
    pass

@app.route('/id/<int:id>', methods=['GET'])
def view():
    pass

@xhr
@app.route('/id/<int:id>', methods=['PUT'])
def edit():
    pass

@xhr
@app.route('/id/<int:id>', methods=['DELETE'])
def delete():
    pass

@app.route('/csrftoken', methods=['GET'])
def csrftoken():
    return generate_csrf()
