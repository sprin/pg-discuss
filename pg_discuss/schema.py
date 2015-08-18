"""
The core schema is intended to be as simple as possible, defining only the
attributes that are absolutely necessary for minimal, relational comment
objects.

Thread schema:

 - id: Primary key.
 - name: Any string identifier defined by the client. Could be a URI, slug, or
   title. Client uses this to fetch comments associated with a thread.

Comment schema:

 - id: Primary key.
 - tid: Foreign key to thread.
 - parent: Foreign key to parent comment.
 - active: Boolean indicating whether comment is included in default fetch.
 - created: Creation timestamp.
 - modified: Modified timestamp.
 - text: The comment text itself.
 - custom_json

custom_json is intended for custom attributes. As a JSON blob, the schema is
flexible and can be extended without requiring database migrations or changes to
the core code. Some possible uses:

 - email
 - website
 - likes/dislikes
 - moderation status (pending, approved, deleted)
"""
from .app import db


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer)
    parent = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    text = db.Column(db.String)
    custom_json = db.Column(db.JSONB)
