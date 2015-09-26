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
flexible and can be extended without requiring database migrations or changes
to the core code. Some possible uses:

 - email
 - website
 - archived flag
 - deleted flag
 - moderated flag
"""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import (
    backref,
    relationship,
)
from sqlalchemy.dialects.postgresql import JSONB

from .db import db


class Thread(db.Model):
    """Thread model."""
    id = Column(
        Integer,
        primary_key=True)
    client_id = Column(
        String,
        unique=True)
    created = Column(
        DateTime(timezone=True),
        server_default=text('NOW()'),
        nullable=False)
    custom_json = Column(
        JSONB,
        server_default='{}',
        nullable=False)

    def __unicode__(self):
        return self.client_id
    __str__ = __unicode__


class Comment(db.Model):
    """Comment model."""
    id = Column(
        Integer,
        primary_key=True,
        nullable=False)
    identity_id = Column(
        Integer,
        ForeignKey('identity.id'),
        nullable=True)
    thread_id = Column(
        Integer,
        ForeignKey('thread.id'),
        nullable=False)
    parent_id = Column(
        Integer,
        ForeignKey('comment.id'))
    version_of_id = Column(
        Integer,
        ForeignKey('comment.id'),
        nullable=True)
    created = Column(
        DateTime(timezone=True),
        server_default=text('NOW()'),
        nullable=False)
    modified = Column(
        DateTime(timezone=True),
        server_default=text('NOW()'),
        nullable=False)
    text = Column(
        String,
        nullable=False)
    custom_json = Column(
        JSONB,
        server_default='{}',
        nullable=False)
    identity = relationship(
        'Identity',
        backref=backref('comments', cascade='all, delete-orphan'))
    thread = relationship(
        'Thread',
        backref=backref('comments', cascade='all, delete-orphan'))

    def __unicode__(self):
        return '<{}> {}'.format(self.identity, self.text[:40])
    __str__ = __unicode__


class Identity(db.Model):
    """Identity model."""
    id = Column(
        Integer,
        primary_key=True,
        nullable=False)
    created = Column(
        DateTime(timezone=True),
        server_default=text('NOW()'),
        nullable=False)
    custom_json = Column(
        JSONB,
        server_default='{}',
        nullable=False)

    def __unicode__(self):
        return '({}) {}'.format(self.id, self.custom_json)
    __str__ = __unicode__


class IdentityToCommentAssociation(db.Model):
    """Association table between Identities and Comments, which may be used to
    by extensions to represent many-to-many relationships such as
    "upvotes"/"downvotes".

    This model is not utilized by the pg-discuss core.
    """
    __tablename__ = 'identity_to_comment'
    id = Column(
        Integer,
        primary_key=True,
        nullable=False)
    identity_id = Column(
        Integer,
        ForeignKey('identity.id'),
        nullable=False)
    comment_id = Column(
        Integer,
        ForeignKey('comment.id'),
        nullable=False)
    rel_type = Column(
        String,
        nullable=False)
    created = Column(
        DateTime(timezone=True),
        server_default=text('NOW()'),
        nullable=False)
    custom_json = Column(
        JSONB,
        server_default='{}',
        nullable=False)
    __table_args__ = (
        UniqueConstraint(
            'identity_id',
            'comment_id',
            'rel_type',
            name='_comment_identity_uc'),
    )
    identity = relationship(
        "Identity",
        backref=backref(
            'identity_to_comments_association',
            cascade='all, delete-orphan'))
    comment = relationship(
        "Comment",
        backref=backref(
            'identity_to_comments_association',
            cascade='all, delete-orphan'))

    def __unicode__(self):
        return '<{}> {} <{}>'.format(self.identity, self.rel_type,
                                     self.comment)
    __str__ = __unicode__


class AdminUser(db.Model):
    """Model for managing admin user authentication.

    This model is not for general user authentication. If traditional
    username/password authentication is desired, it must be implemented as
    an `IdentityPolicy` with its own model.
    """
    __tablename__ = 'admin_user'
    id = Column(
        Integer,
        primary_key=True,
        nullable=False)
    login = Column(
        String,
        unique=True,
        nullable=False)
    email = Column(
        String,
        nullable=False)
    active = Column(
        Boolean,
        nullable=False)
    password = Column(
        String,
        nullable=False)

    # Flask-Login integration
    def is_authenticated(self):
        """Is this user authenticated? Always True."""
        return True

    def is_active(self):
        """Is this user active?"""
        return self.active

    def is_anonymous(self):
        """Is this user anonymous? Always False."""
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username
    __str__ = __unicode__
