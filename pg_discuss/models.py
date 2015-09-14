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
 - created: Creation timestamp.
 - modified: Modified timestamp.
 - text: The comment text itself.
 - custom_json

custom_json is intended for custom attributes. As a JSON blob, the schema is
flexible and can be extended without requiring database migrations or changes to
the core code. Some possible uses:

 - email
 - website
 - archived flag
 - deleted flag
 - moderated flag
 - likes/dislikes
"""
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

class PgAlchemy(SQLAlchemy):
    """Custom subclass of the SQLAlchemy extension that sets the
    connection timezone to UTC. The backend should handle timestamps entirely
    in UTC, with timezone adjustment performed on the client side.
    """
    def apply_driver_hacks(self, app, info, options):
        options['connect_args'] = {"options": "-c timezone=utc"}
        options['isolation_level'] = 'AUTOCOMMIT'

db = PgAlchemy()

class Thread(db.Model):
    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    created = Column(DateTime(timezone=True), server_default=text('NOW()'), nullable=False)
    custom_json = Column(JSONB, server_default='{}', nullable=False)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    identity_id = Column(Integer, ForeignKey('identity.id'), nullable=True)
    thread_id = Column(Integer, ForeignKey('thread.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comment.id'))
    version_of_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    created = Column(DateTime(timezone=True), server_default=text('NOW()'), nullable=False)
    modified = Column(DateTime(timezone=True), server_default=text('NOW()'), nullable=False)
    text = Column(String, nullable=False)
    custom_json = Column(JSONB, server_default='{}', nullable=False)


class Identity(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    created = Column(DateTime(timezone=True), server_default=text('NOW()'), nullable=False)
    custom_json = Column(JSONB, server_default='{}', nullable=False)


class IdentityToComment(db.Model):
    __tablename__ = 'identity_to_comment'
    id = Column(Integer, primary_key=True, nullable=False)
    identity_id = Column(Integer, ForeignKey('identity.id'), nullable=False)
    comment_id = Column(Integer, ForeignKey('comment.id'), nullable=False)
    rel_type = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), server_default=text('NOW()'), nullable=False)
    custom_json = Column(JSONB, server_default='{}', nullable=False)
    __table_args__ = (UniqueConstraint('identity_id', 'comment_id', 'rel_type',
                                       name='_comment_identity_uc'),)
