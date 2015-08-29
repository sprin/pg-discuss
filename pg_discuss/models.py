"""
The core schema is intended to be as simple as possible, defining only the
attributes that are absolutely necessary for minimal, relational comment
objects.

Thread schema:

 - id: Primary key.
 - client_id: String used as unique identifier by client.
 - custom_json

`client_id` must have a value which is *immutable*.  Client uses this to
create the initial thread and fetch comments associated with a thread.

URI, title, slug are *not* recommended because these values may change (page
may move to different domain, title/slug may be edited).

Recommended: For many static site generators, a client_id can be defined in
custom metadata. The client_id can be set to a UUID generated at the time of
initial article creation (using a text editor plugin, or manually using a CLI
tool such as uuidgen). The static site generator can then render this in to an
HTML data attribute for extraction by the client.

Comment schema:

 - id: Primary key.
 - thread_id: Foreign key to thread.
 - parent_id: Foreign key to parent comment.
 - version_of_id: Foreign key to the comment of which this comment is a
   version. Used by extensions that preserve comment versions.
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
    ForeignKey,
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
    client_id = Column(String, unique=True)
    custom_json = Column(JSONB, server_default='{}', nullable=False)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('thread.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comment.id'))
    version_of_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    active = Column(Boolean, server_default='TRUE', nullable=False)
    created = Column(DateTime, server_default=text('NOW()'), nullable=False)
    modified = Column(DateTime, server_default=text('NOW()'), nullable=False)
    text = Column(String, nullable=False)
    custom_json = Column(JSONB, server_default='{}', nullable=False)
