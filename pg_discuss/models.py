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
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Thread(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    tid = Column(Integer, nullable=False)
    parent = Column(Integer)
    active = Column(Boolean, server_default='TRUE', nullable=False)
    archived_from = Column(Integer)
    created = Column(DateTime, server_default=text('NOW()'), nullable=False)
    modified = Column(DateTime, server_default=text('NOW()'), nullable=False)
    text = Column(String, nullable=False)
    custom_json = Column(JSONB, server_default='{}', nullable=False)
