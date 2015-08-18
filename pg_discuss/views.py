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
)

from pg_discuss.csrf import generate_csrf
from pg_discuss import tables
from pg_discuss.models import db

def fetch():
    pass

def new():
    pass

def view():
    pass

def edit():
    pass

def delete():
    pass

def csrftoken():
    return generate_csrf()
